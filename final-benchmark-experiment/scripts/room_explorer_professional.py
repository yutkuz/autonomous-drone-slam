#!/usr/bin/env python3
import argparse
import math
import struct
import time
import collections

import rclpy
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from rclpy.node import Node
from sensor_msgs.msg import PointCloud2
from std_msgs.msg import Empty

# Sıkışma tespiti: son N saniyede toplam yer değiştirme bu metrenin altındaysa sıkışmış sayılır
STUCK_WINDOW   = 15.0  # saniye
STUCK_DIST     = 0.50  # metre — bu kadar hareket etmediyse sıkışmış
RECOVERY_BACK  = 2.5   # saniye geri git
RECOVERY_TURN  = 3.5   # saniye dön


class ProfessionalRoomExplorer(Node):
    def __init__(self, args):
        super().__init__("v12_professional_room_explorer", parameter_overrides=[
            rclpy.parameter.Parameter("use_sim_time", rclpy.Parameter.Type.BOOL, True)
        ])
        self.args = args
        self.takeoff_pub = self.create_publisher(Empty, "/simple_drone/takeoff", 10)
        self.land_pub    = self.create_publisher(Empty, "/simple_drone/land", 10)
        self.cmd_pub     = self.create_publisher(Twist, "/simple_drone/cmd_vel", 10)

        self.x = 0.0
        self.y = 0.0
        self.z = 0.0
        self.yaw = 0.0
        self.front = 999.0
        self.left  = 999.0
        self.right = 999.0

        self.flying     = False
        self.escape     = False
        self.start_time = time.monotonic()
        self.last_takeoff = 0.0
        self.log_counter  = 0

        # Sıkışma tespiti
        # Deque: (zaman, x, y) çiftlerini saklar
        self.pos_history = collections.deque()
        self.last_pos_record = 0.0

        # Kurtarma modu
        self.recovery_mode  = False          # True iken kurtarma manevraları yapılır
        self.recovery_phase = 'back'         # 'back' → geri, 'turn' → dön
        self.recovery_start = 0.0
        self.recovery_turn_dir = 1.0         # +1 sol, -1 sağ (her kurtarmada değişir)
        self.recovery_count = 0              # kaç kez kurtarma yapıldı

        self.create_subscription(Odometry, "/simple_drone/odom", self.odom_cb, 10)
        self.create_subscription(PointCloud2, "/simple_drone/lidar3d/points", self.lidar_cb, 10)
        self.timer = self.create_timer(0.1, self.loop)
        self.get_logger().info(
            "Final benchmark explorer baslatildi: sikisma kurtarma aktif, "
            f"esik={STUCK_DIST}m/{STUCK_WINDOW}s"
        )

    # ------------------------------------------------------------------ callbacks

    def odom_cb(self, msg):
        self.x = float(msg.pose.pose.position.x)
        self.y = float(msg.pose.pose.position.y)
        self.z = float(msg.pose.pose.position.z)
        q = msg.pose.pose.orientation
        self.yaw = math.atan2(
            2.0 * (q.w * q.z + q.x * q.y),
            1.0 - 2.0 * (q.y * q.y + q.z * q.z),
        )

    def lidar_cb(self, msg):
        front, left, right = [], [], []
        data = bytes(msg.data)
        step = msg.point_step
        total = msg.width * msg.height
        for i in range(0, total, self.args.lidar_stride):
            offset = i * step
            if offset + 12 > len(data):
                break
            x = struct.unpack_from("f", data, offset)[0]
            y = struct.unpack_from("f", data, offset + 4)[0]
            z = struct.unpack_from("f", data, offset + 8)[0]
            if not (math.isfinite(x) and math.isfinite(y) and math.isfinite(z)):
                continue
            if z < -0.45 or z > 1.05:
                continue
            d = math.hypot(x, y)
            if d < 0.35 or d > self.args.lidar_max:
                continue
            angle = math.degrees(math.atan2(y, x))
            if -25 <= angle <= 25:
                front.append(d)
            elif 45 <= angle <= 135:
                left.append(d)
            elif -135 <= angle <= -45:
                right.append(d)
        self.front = min(front) if front else 999.0
        self.left  = min(left)  if left  else 999.0
        self.right = min(right) if right else 999.0

    # ------------------------------------------------------------------ helpers

    def altitude_cmd(self, target):
        return max(-self.args.vertical_speed,
                   min(self.args.vertical_speed,
                       self.args.altitude_gain * (target - self.z)))

    def publish_takeoff_until_ready(self):
        now = time.monotonic()
        if now - self.last_takeoff > 0.6 and self.z < self.args.altitude - 0.35:
            self.takeoff_pub.publish(Empty())
            self.last_takeoff = now

    def record_position(self):
        now = time.monotonic()
        if now - self.last_pos_record >= 1.0:
            self.pos_history.append((now, self.x, self.y))
            self.last_pos_record = now
        # Eski kayıtları temizle
        cutoff = now - STUCK_WINDOW
        while self.pos_history and self.pos_history[0][0] < cutoff:
            self.pos_history.popleft()

    def is_stuck(self):
        if len(self.pos_history) < int(STUCK_WINDOW * 0.6):
            return False   # Henüz yeterli veri yok
        oldest = self.pos_history[0]
        dx = self.x - oldest[1]
        dy = self.y - oldest[2]
        return math.hypot(dx, dy) < STUCK_DIST

    def start_recovery(self):
        self.recovery_mode  = True
        self.recovery_phase = 'back'
        self.recovery_start = time.monotonic()
        self.recovery_turn_dir *= -1      # Her seferinde ters yöne dön
        self.recovery_count += 1
        self.pos_history.clear()          # Sayacı sıfırla
        self.get_logger().warn(
            f"SIKISMA TESPIT EDILDI (#{self.recovery_count})! "
            f"Kurtarma: geri {RECOVERY_BACK}s + "
            f"{'sol' if self.recovery_turn_dir > 0 else 'sag'} dönüş {RECOVERY_TURN}s"
        )

    def run_recovery(self, cmd):
        now = time.monotonic()
        elapsed = now - self.recovery_start

        if self.recovery_phase == 'back':
            cmd.linear.x = -self.args.forward_speed * 1.5   # geri
            cmd.linear.z = self.altitude_cmd(self.args.altitude)
            if elapsed > RECOVERY_BACK:
                self.recovery_phase = 'turn'
                self.recovery_start = now
                self.get_logger().info("Kurtarma: geri bitti, dönüş başlıyor.")
        else:  # 'turn'
            cmd.angular.z = self.args.turn_speed * 1.5 * self.recovery_turn_dir
            cmd.linear.z  = self.altitude_cmd(self.args.altitude)
            if elapsed > RECOVERY_TURN:
                self.recovery_mode = False
                self.get_logger().info("Kurtarma tamamlandi, normal kesife devam.")

        self.cmd_pub.publish(cmd)

    # ------------------------------------------------------------------ main loop

    def loop(self):
        self.log_counter += 1
        elapsed = time.monotonic() - self.start_time

        # Süre doldu mu?
        if self.args.duration > 0 and elapsed > self.args.duration:
            self.cmd_pub.publish(Twist())
            self.get_logger().info("Kesif suresi doldu, drone durduruluyor.")
            rclpy.shutdown()
            return

        self.publish_takeoff_until_ready()
        cmd = Twist()

        # Kalkış
        if not self.flying:
            cmd.linear.z = self.altitude_cmd(self.args.altitude)
            self.cmd_pub.publish(cmd)
            if abs(self.z - self.args.altitude) < 0.22:
                self.flying = True
                self.get_logger().info("Hedef irtifada, haritalama rotasi basliyor.")
            return

        # Pozisyon geçmişi kaydet
        self.record_position()

        # Kurtarma modundaysa devam et
        if self.recovery_mode:
            self.run_recovery(cmd)
            return

        # Sıkışma kontrolü (sadece aktif uçuşta, escape değilken)
        if self.flying and not self.escape and self.is_stuck():
            self.start_recovery()
            return

        # Normal uçuş
        target_z = self.args.altitude + (0.7 if self.escape else 0.0)
        cmd.linear.z = self.altitude_cmd(target_z)

        front_blocked = self.front < self.args.front_safe
        left_blocked  = self.left  < self.args.side_blocked
        right_blocked = self.right < self.args.side_blocked

        if self.escape:
            if not front_blocked:
                self.escape = False
                self.get_logger().info("On acildi, normal irtifaya donuluyor.")
            else:
                self.cmd_pub.publish(cmd)
                return

        if not front_blocked:
            cmd.linear.x = self.args.forward_speed
            if self.left < self.args.corridor_range and self.right < self.args.corridor_range:
                cmd.linear.y = max(-self.args.side_speed,
                                   min(self.args.side_speed,
                                       self.args.center_gain * (self.left - self.right)))
        else:
            if left_blocked and right_blocked:
                self.escape = True
                cmd.linear.x = 0.0
                self.get_logger().info("Dar alanda dikey kacis basladi.")
            else:
                cmd.angular.z = self.args.turn_speed if self.left >= self.right else -self.args.turn_speed

        if self.log_counter % 10 == 0:
            self.get_logger().info(
                f"on:{self.front:.2f} sol:{self.left:.2f} sag:{self.right:.2f} "
                f"z:{self.z:.2f} xy:({self.x:.1f},{self.y:.1f}) "
                f"kurtarma:{self.recovery_count} "
                f"{'KACIS' if self.escape else ''}"
            )
        self.cmd_pub.publish(cmd)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--altitude",       type=float, default=1.5)
    parser.add_argument("--duration",       type=float, default=0.0)
    parser.add_argument("--forward-speed",  type=float, default=0.10)
    parser.add_argument("--side-speed",     type=float, default=0.10)
    parser.add_argument("--turn-speed",     type=float, default=0.10)
    parser.add_argument("--vertical-speed", type=float, default=0.10)
    parser.add_argument("--altitude-gain",  type=float, default=0.35)
    parser.add_argument("--front-safe",     type=float, default=1.35)
    parser.add_argument("--side-blocked",   type=float, default=0.75)
    parser.add_argument("--corridor-range", type=float, default=3.0)
    parser.add_argument("--center-gain",    type=float, default=0.22)
    parser.add_argument("--lidar-max",      type=float, default=8.0)
    parser.add_argument("--lidar-stride",   type=int,   default=8)
    args = parser.parse_args()

    rclpy.init()
    node = ProfessionalRoomExplorer(args)
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.cmd_pub.publish(Twist())
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
