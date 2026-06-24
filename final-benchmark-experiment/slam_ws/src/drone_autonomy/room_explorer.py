#!/usr/bin/env python3
# Tepkisel kesif: koridor-dostu duvar takibi + dikey kacis.
# - Yan duvarlar ENGEL DEGIL: iki yanda duvar varsa ortalanip duz gider.
# - Sadece ON kapaninca tepki verir, daha acik tarafa doner.
# - Hem on hem iki yan kapaliysa yukari kacar, on acilinca eski irtifaya doner.

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import Empty
from sensor_msgs.msg import PointCloud2
from nav_msgs.msg import Odometry
import struct
import math
import time


class RoomExplorer(Node):
    def __init__(self):
        super().__init__('room_explorer', parameter_overrides=[
            rclpy.parameter.Parameter('use_sim_time', rclpy.Parameter.Type.BOOL, True)
        ])
        self.takeoff_pub = self.create_publisher(Empty, '/simple_drone/takeoff', 10)
        self.land_pub = self.create_publisher(Empty, '/simple_drone/land', 10)
        self.cmd_vel_pub = self.create_publisher(Twist, '/simple_drone/cmd_vel', 10)

        # Durum
        self.pos_z = 0.0
        self.yaw = 0.0
        self.front = 999.0
        self.left = 999.0
        self.right = 999.0

        # Parametreler
        self.target_z = 1.5          # hedef ucus irtifasi
        self.forward_speed = 0.12       # duz: daha yavas
        self.turn_speed = 0.12          # donus: cok yavas
        self.front_safe = 1.3        # bundan yakin ON engeli = donus
        self.side_blocked = 0.8      # yan bu kadar yakinsa "kapali" sayilir
        self.corridor_range = 3.0    # iki yanda duvar varsa ortala
        self.center_gain = 0.25      # ortalama (strafe) kazanci

        # Dikey kacis
        self.escape = False
        self.escape_return_z = self.target_z

        # Takeoff / irtifa
        self.flying = False
        for _ in range(5):
            self.takeoff_pub.publish(Empty())

        self.create_subscription(PointCloud2, '/simple_drone/lidar3d/points', self.lidar_cb, 10)
        self.create_subscription(Odometry, '/simple_drone/odom', self.odom_cb, 10)
        self.timer = self.create_timer(0.1, self.loop)
        self.log = 0
        self.get_logger().info('Tepkisel kesif basladi (koridor-dostu).')

    def odom_cb(self, msg):
        self.pos_z = msg.pose.pose.position.z
        q = msg.pose.pose.orientation
        self.yaw = math.atan2(2.0 * (q.w * q.z + q.x * q.y),
                              1.0 - 2.0 * (q.y * q.y + q.z * q.z))

    def lidar_cb(self, msg):
        f, l, r = [], [], []
        data = bytes(msg.data)
        step = msg.point_step
        n = msg.width * msg.height
        for i in range(0, n, 8):   # her 8. nokta: CPU yuku 8 kat azalir
            o = i * step
            if o + 12 > len(data):
                break
            x = struct.unpack_from('f', data, o)[0]
            y = struct.unpack_from('f', data, o + 4)[0]
            z = struct.unpack_from('f', data, o + 8)[0]
            if math.isnan(x) or math.isnan(y) or math.isnan(z):
                continue
            if z < -0.4 or z > 1.0:
                continue
            d = math.hypot(x, y)
            if d < 0.4 or d > 8.0:
                continue
            a = math.degrees(math.atan2(y, x))
            if -25 <= a <= 25:
                f.append(d)
            elif 45 <= a <= 135:
                l.append(d)
            elif -135 <= a <= -45:
                r.append(d)
        self.front = min(f) if f else 999.0
        self.left = min(l) if l else 999.0
        self.right = min(r) if r else 999.0

    def loop(self):
        self.log += 1
        should_log = (self.log % 10 == 0)

        # Irtifaya cik (kalkis sonrasi)
        if not self.flying:
            if self.pos_z >= self.target_z - 0.3:
                self.flying = True
                self.get_logger().info('Hedef irtifada, kesif basliyor.')
            else:
                t = Twist()
                t.linear.z = 0.15
                self.cmd_vel_pub.publish(t)
            return

        t = Twist()
        # Irtifa korumasi (her durumda)
        z_target = self.escape_return_z if not self.escape else self.target_z + 1.2
        t.linear.z = max(-0.1, min(0.1, 0.4 * (z_target - self.pos_z)))

        front_blocked = self.front < self.front_safe
        left_blocked = self.left < self.side_blocked
        right_blocked = self.right < self.side_blocked

        # --- Dikey kacis modu ---
        if self.escape:
            if not front_blocked:                      # on acildi -> geri don
                self.escape = False
                self.get_logger().info('On acildi, eski irtifaya donuluyor.')
            else:
                t.linear.x = 0.0                        # yukari cikmaya devam
                self.cmd_vel_pub.publish(t)
                return

        if not front_blocked:
            # ON ACIK: duz ilerle, koridordaysa ortala (panik yok)
            t.linear.x = self.forward_speed
            if self.left < self.corridor_range and self.right < self.corridor_range:
                # iki yanda da duvar -> ortala (sol-sag farkina gore yana kay)
                t.linear.y = max(-0.15, min(0.15,
                                 self.center_gain * (self.left - self.right)))
        else:
            # ON KAPALI
            if left_blocked and right_blocked:
                # gercekten sikisti -> dikey kacis
                self.escape = True
                self.escape_return_z = self.pos_z
                self.get_logger().info('Sikisti! Yukari kacis...')
            else:
                # daha acik tarafa don
                if self.left >= self.right:
                    t.angular.z = self.turn_speed       # sola
                else:
                    t.angular.z = -self.turn_speed      # saga
                t.linear.x = 0.0

        if should_log:
            self.get_logger().info(
                f'on:{self.front:.1f} sol:{self.left:.1f} sag:{self.right:.1f} '
                f'z:{self.pos_z:.1f} {"KACIS" if self.escape else ""}')
        self.cmd_vel_pub.publish(t)


def main():
    rclpy.init()
    node = RoomExplorer()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.cmd_vel_pub.publish(Twist())
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()