#!/usr/bin/env python3
"""
Final benchmark waypoint explorer
Kapali loop galeri rotasini dusuk hizla takip eder.

Rota (feature_loop_gallery):
  Dis galeri loop'u iki kez tarar, sonra merkez adanin etrafinda yakin tur atar.
"""
import argparse, math, time
import rclpy
from rclpy.node import Node
from rclpy.executors import ExternalShutdownException
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from std_msgs.msg import Empty

# ── Waypoint listesi (x, y) metre ──────────────────────────────────────────
# Genis koridor merkezleri. Kapali loop, RTAB-Map loop closure icin ayni bolgeleri tekrar gorur.
WAYPOINTS = [
    (-6.2, -4.6), (-4.0, -4.6), (-1.8, -4.6), (0.5, -4.6),
    ( 2.8, -4.6), ( 5.0, -4.6), (6.2, -3.4), (6.2, -1.2),
    ( 6.2,  1.2), ( 6.2,  3.4), (5.0,  4.6), (2.8,  4.6),
    ( 0.5,  4.6), (-1.8,  4.6), (-4.0,  4.6), (-6.2,  4.6),
    (-6.2,  2.3), (-6.2,  0.0), (-6.2, -2.3), (-6.2, -4.6),

    (-4.0, -4.6), (-1.8, -4.6), (0.5, -4.6), (2.8, -4.6),
    ( 5.0, -4.6), (6.2, -3.4), (6.2, -1.2), (6.2,  1.2),
    ( 6.2,  3.4), (5.0,  4.6), (2.8,  4.6), (0.5,  4.6),
    (-1.8,  4.6), (-4.0,  4.6), (-6.2,  4.6), (-6.2,  2.3),
    (-6.2,  0.0), (-6.2, -2.3), (-6.2, -4.6),

    (-4.0, -3.35), (0.0, -3.35), (4.0, -3.35),
    (4.0,  3.35), (0.0,  3.35), (-4.0,  3.35),
    (-4.0, -3.35), (-6.2, -4.6),
]

REACH_DIST  = 0.80  # stabil kabul mesafesi (m)
MAX_SPEED   = 0.30  # daha temiz SLAM icin yavas hiz (m/s)
TURN_GAIN   = 1.0   # yaw hizalama kazanci
POS_GAIN    = 0.48  # pozisyon kazanci


class WaypointExplorer(Node):
    def __init__(self, args):
        super().__init__("final_benchmark_waypoint_explorer", parameter_overrides=[
            rclpy.parameter.Parameter("use_sim_time", rclpy.Parameter.Type.BOOL, True)
        ])
        self.args = args
        self.takeoff_pub = self.create_publisher(Empty, "/simple_drone/takeoff", 10)
        self.cmd_pub     = self.create_publisher(Twist, "/simple_drone/cmd_vel", 10)

        self.x = self.y = self.z = self.yaw = 0.0
        self.flying      = False
        self.wp_idx      = 0
        self.start_time  = time.monotonic()
        self.last_takeoff = 0.0
        self.log_counter  = 0
        self.done         = False

        self.create_subscription(Odometry, "/simple_drone/odom", self.odom_cb, 10)
        self.timer = self.create_timer(0.1, self.loop)

        self.get_logger().info(
            f"Waypoint gezici basladi — {len(WAYPOINTS)} nokta, "
            f"hiz={MAX_SPEED}m/s, sure={args.duration}s"
        )

    # ── callbacks ────────────────────────────────────────────────────────────

    def odom_cb(self, msg):
        self.x = msg.pose.pose.position.x
        self.y = msg.pose.pose.position.y
        self.z = msg.pose.pose.position.z
        q = msg.pose.pose.orientation
        self.yaw = math.atan2(
            2*(q.w*q.z + q.x*q.y),
            1 - 2*(q.y*q.y + q.z*q.z)
        )

    # ── helpers ──────────────────────────────────────────────────────────────

    def try_takeoff(self):
        now = time.monotonic()
        if now - self.last_takeoff > 0.6 and self.z < self.args.altitude - 0.35:
            self.takeoff_pub.publish(Empty())
            self.last_takeoff = now

    def clamp(self, v, limit):
        return max(-limit, min(limit, v))

    # ── main loop ─────────────────────────────────────────────────────────────

    def loop(self):
        self.log_counter += 1
        elapsed = time.monotonic() - self.start_time

        if self.done:
            return

        # Süre doldu
        if self.args.duration > 0 and elapsed > self.args.duration:
            self.cmd_pub.publish(Twist())
            self.get_logger().info("Sure doldu, duruyorum.")
            self.done = True
            rclpy.try_shutdown()
            return

        self.try_takeoff()

        # Kalkış aşaması
        if not self.flying:
            cmd = Twist()
            err = self.args.altitude - self.z
            cmd.linear.z = self.clamp(0.4 * err, 0.15)
            self.cmd_pub.publish(cmd)
            if abs(err) < 0.22:
                self.flying = True
                self.get_logger().info(
                    f"Irtifada ({self.z:.2f}m), waypoint rotasina baslanıyor."
                )
            return

        # Tüm waypoint'ler tamamlandı — yerinde bekle
        if self.wp_idx >= len(WAYPOINTS):
            self.cmd_pub.publish(Twist())
            if self.log_counter % 50 == 0:
                self.get_logger().info("Tüm waypoint'ler tamamlandi, bekliyorum.")
            return

        # Hedef waypoint
        tx, ty = WAYPOINTS[self.wp_idx]
        dx = tx - self.x
        dy = ty - self.y
        dist = math.hypot(dx, dy)

        # Waypoint'e ulaştı mı?
        if dist < REACH_DIST:
            self.get_logger().info(
                f"WP {self.wp_idx+1}/{len(WAYPOINTS)} tamam "
                f"({tx:.1f},{ty:.1f})  —  sonraki: "
                + (f"({WAYPOINTS[self.wp_idx+1][0]:.1f},{WAYPOINTS[self.wp_idx+1][1]:.1f})"
                   if self.wp_idx+1 < len(WAYPOINTS) else "bitti")
            )
            self.wp_idx += 1
            return

        # Hedefe giden world-frame hizini drone body-frame cmd_vel'e cevir.
        # sjtu_drone cmd_vel body frame bekliyor; direkt world hiz vermek duvara sapmaya sebep olur.
        speed = min(MAX_SPEED, POS_GAIN * dist)
        vx_world = speed * dx / (dist + 1e-6)
        vy_world = speed * dy / (dist + 1e-6)
        cy = math.cos(self.yaw)
        sy = math.sin(self.yaw)
        cmd = Twist()
        cmd.linear.x = self.clamp(cy * vx_world + sy * vy_world, MAX_SPEED)
        cmd.linear.y = self.clamp(-sy * vx_world + cy * vy_world, MAX_SPEED)
        cmd.linear.z = self.clamp(0.4 * (self.args.altitude - self.z), 0.12)
        # Drone'u hedef yönüne döndür (görsel için, hareket için şart değil)
        target_yaw = math.atan2(dy, dx)
        yaw_err = target_yaw - self.yaw
        while yaw_err >  math.pi: yaw_err -= 2*math.pi
        while yaw_err < -math.pi: yaw_err += 2*math.pi
        cmd.angular.z = self.clamp(TURN_GAIN * yaw_err, 0.5)

        self.cmd_pub.publish(cmd)

        if self.log_counter % 15 == 0:
            self.get_logger().info(
                f"WP {self.wp_idx+1}/{len(WAYPOINTS)} "
                f"hedef=({tx:.1f},{ty:.1f}) "
                f"konum=({self.x:.1f},{self.y:.1f}) "
                f"mesafe={dist:.2f}m  z={self.z:.2f}"
            )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--altitude", type=float, default=1.5)
    parser.add_argument("--duration", type=float, default=0.0)
    args = parser.parse_args()

    rclpy.init()
    node = WaypointExplorer(args)
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        if rclpy.ok():
            node.cmd_pub.publish(Twist())
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
