#!/usr/bin/env python3
import argparse
import math
import time
from dataclasses import dataclass

import rclpy
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from std_msgs.msg import Empty


MAX_SPEED = 0.24
POS_GAIN = 0.42
TURN_GAIN = 1.05
REACH_DIST = 0.92
NEAR_COVERED_DIST = 1.15
GRID_SIZE = 0.8


@dataclass
class Target:
    x: float
    y: float
    mode: str = "move"  # move | scan
    yaw: float | None = None


def build_coverage_targets():
    targets = []

    # Dis cevre: once duvarlari yakin ve kapali loop seklinde gor.
    outer = [
        (-6.2, -4.6), (-3.8, -4.6), (-1.4, -4.6), (1.0, -4.6), (3.4, -4.6), (5.8, -4.2),
        (6.2, -2.0), (6.2, 0.4), (6.2, 2.8), (5.6, 4.5), (3.2, 4.6), (0.8, 4.6),
        (-1.6, 4.6), (-4.0, 4.6), (-6.2, 4.2), (-6.2, 1.8), (-6.2, -0.6), (-6.2, -3.0),
        (-6.2, -4.6),
    ]
    for i, (x, y) in enumerate(outer):
        targets.append(Target(x, y))
        if i in {2, 5, 8, 11, 14, 17}:
            targets.append(Target(x, y, mode="scan"))

    # Ic tarama: merkezi yapiya carpmamak icin sol/sag koridorlari ayri gez.
    # Onceki denemede orta serit hedefleri drone'u engel kenarinda kilitledi.
    right_sweep = [
        (4.8, -3.4), (3.1, -3.4), (3.1, -1.2), (4.9, -1.2),
        (4.9, 1.2), (3.1, 1.2), (3.1, 3.4), (4.8, 3.4),
    ]
    left_sweep = [
        (-4.8, 3.4), (-3.1, 3.4), (-3.1, 1.2), (-4.9, 1.2),
        (-4.9, -1.2), (-3.1, -1.2), (-3.1, -3.4), (-4.8, -3.4),
    ]

    for i, (x, y) in enumerate(right_sweep):
        targets.append(Target(x, y))
        if i in {1, 3, 5, 7}:
            targets.append(Target(x, y, mode="scan"))

    # Sol tarafa gecis icin ust koridoru kullan; orta engelin icinden kestirme yapma.
    bridge = [(4.8, 4.3), (1.6, 4.6), (-1.6, 4.6), (-4.8, 4.3)]
    for x, y in bridge:
        targets.append(Target(x, y))

    for i, (x, y) in enumerate(left_sweep):
        targets.append(Target(x, y))
        if i in {1, 3, 5, 7}:
            targets.append(Target(x, y, mode="scan"))

    # Son kapanis: alt ve yan duvarlari ikinci kez gor, loop closure sansini arttir.
    closure = [(-5.9, -4.0), (-2.5, -4.6), (0.0, -4.6), (2.5, -4.6), (5.9, -4.0), (5.9, 0.0)]
    for i, (x, y) in enumerate(closure):
        targets.append(Target(x, y))
        if i in {1, 3, 5}:
            targets.append(Target(x, y, mode="scan"))

    return targets


class CoverageExplorer(Node):
    def __init__(self, args):
        super().__init__("final_benchmark_coverage_explorer", parameter_overrides=[
            rclpy.parameter.Parameter("use_sim_time", rclpy.Parameter.Type.BOOL, True)
        ])
        self.args = args
        self.takeoff_pub = self.create_publisher(Empty, "/simple_drone/takeoff", 10)
        self.cmd_pub = self.create_publisher(Twist, "/simple_drone/cmd_vel", 10)
        self.create_subscription(Odometry, "/simple_drone/odom", self.odom_cb, 10)

        self.targets = build_coverage_targets()
        self.idx = 0
        self.x = self.y = self.z = self.yaw = 0.0
        self.start_time = time.monotonic()
        self.last_takeoff = 0.0
        self.flying = False
        self.done = False
        self.log_counter = 0
        self.visited = {}
        self.blacklisted = set()
        self.failed_targets = set()

        self.scan_until = 0.0
        self.scan_start = 0.0
        self.recovery_until = 0.0
        self.recovery_phase = 0

        self.progress_window_start = time.monotonic()
        self.progress_window_pos = (0.0, 0.0)
        self.last_target_change = time.monotonic()
        self.best_dist_for_target = 999.0

        self.timer = self.create_timer(0.1, self.loop)
        self.get_logger().info(
            f"Coverage explorer basladi: {len(self.targets)} otomatik hedef, "
            f"hiz={MAX_SPEED}m/s, sure={args.duration}s"
        )

    def odom_cb(self, msg):
        self.x = msg.pose.pose.position.x
        self.y = msg.pose.pose.position.y
        self.z = msg.pose.pose.position.z
        q = msg.pose.pose.orientation
        self.yaw = math.atan2(
            2 * (q.w * q.z + q.x * q.y),
            1 - 2 * (q.y * q.y + q.z * q.z),
        )

    def clamp(self, v, limit):
        return max(-limit, min(limit, v))

    def grid_key(self, x=None, y=None):
        x = self.x if x is None else x
        y = self.y if y is None else y
        return (round(x / GRID_SIZE), round(y / GRID_SIZE))

    def mark_visited(self):
        key = self.grid_key()
        self.visited[key] = self.visited.get(key, 0) + 1

    def try_takeoff(self):
        now = time.monotonic()
        if now - self.last_takeoff > 0.6 and self.z < self.args.altitude - 0.35:
            self.takeoff_pub.publish(Empty())
            self.last_takeoff = now

    def advance_target(self, reason):
        if self.idx < len(self.targets):
            t = self.targets[self.idx]
            if reason in {"ilerleme yok", "engel yakin"}:
                self.failed_targets.add(self.grid_key(t.x, t.y))
            self.get_logger().info(
                f"Hedef {self.idx+1}/{len(self.targets)} gecildi ({reason}): "
                f"({t.x:.1f},{t.y:.1f}) mode={t.mode}"
            )
        self.idx += 1
        self.last_target_change = time.monotonic()
        self.best_dist_for_target = 999.0

    def start_scan(self):
        now = time.monotonic()
        self.scan_start = now
        self.scan_until = now + 5.0
        self.get_logger().info("Yaw scan basladi: bulut yogunlugu icin 5 sn yavas donus.")

    def start_recovery(self):
        now = time.monotonic()
        self.recovery_until = now + 3.2
        self.recovery_phase += 1
        self.get_logger().warn("Stuck algilandi: recovery manevrasi ve hedef degisimi.")

    def in_recovery(self, now):
        return now < self.recovery_until

    def run_recovery(self, now):
        cmd = Twist()
        remaining = self.recovery_until - now
        cmd.linear.z = self.clamp(0.35 * (self.args.altitude - self.z), 0.10)
        if remaining > 2.0:
            cmd.linear.x = -0.16
            cmd.angular.z = 0.35
        elif remaining > 1.0:
            cmd.linear.y = 0.18 if self.recovery_phase % 2 else -0.18
            cmd.angular.z = -0.45
        else:
            cmd.linear.x = 0.12
            cmd.angular.z = 0.25
        self.cmd_pub.publish(cmd)

    def run_scan(self, now):
        cmd = Twist()
        cmd.linear.z = self.clamp(0.35 * (self.args.altitude - self.z), 0.08)
        cmd.angular.z = 0.42
        self.cmd_pub.publish(cmd)
        if now > self.scan_until:
            self.scan_until = 0.0
            self.advance_target("scan tamam")

    def current_target(self):
        while self.idx < len(self.targets):
            t = self.targets[self.idx]
            key = self.grid_key(t.x, t.y)
            if key in self.failed_targets and t.mode == "move":
                self.advance_target("daha once takildi")
                continue
            if t.mode == "move" and self.visited.get(key, 0) > 7:
                self.blacklisted.add(key)
                self.advance_target("cok ziyaret edildi")
                continue
            return t
        return None

    def loop(self):
        self.log_counter += 1
        now = time.monotonic()
        elapsed = now - self.start_time
        self.mark_visited()

        if self.done:
            return

        if self.args.duration > 0 and elapsed > self.args.duration:
            self.cmd_pub.publish(Twist())
            self.get_logger().info("Sure doldu, duruyorum.")
            self.done = True
            rclpy.try_shutdown()
            return

        self.try_takeoff()
        if not self.flying:
            cmd = Twist()
            err = self.args.altitude - self.z
            cmd.linear.z = self.clamp(0.4 * err, 0.15)
            self.cmd_pub.publish(cmd)
            if abs(err) < 0.22:
                self.flying = True
                self.progress_window_start = now
                self.progress_window_pos = (self.x, self.y)
                self.get_logger().info(f"Irtifada ({self.z:.2f}m), coverage basliyor.")
            return

        if self.in_recovery(now):
            self.run_recovery(now)
            return

        if self.scan_until:
            self.run_scan(now)
            return

        target = self.current_target()
        if target is None:
            self.cmd_pub.publish(Twist())
            if self.log_counter % 50 == 0:
                self.get_logger().info("Coverage hedefleri bitti, bekliyorum.")
            return

        if target.mode == "scan":
            self.start_scan()
            return

        dx = target.x - self.x
        dy = target.y - self.y
        dist = math.hypot(dx, dy)
        self.best_dist_for_target = min(self.best_dist_for_target, dist)

        if dist < REACH_DIST:
            self.advance_target("ulasildi")
            return

        moved = math.hypot(self.x - self.progress_window_pos[0], self.y - self.progress_window_pos[1])
        no_progress_for = now - self.progress_window_start
        if no_progress_for > 14.0:
            if moved < 0.55 and dist < NEAR_COVERED_DIST:
                self.advance_target("yeterince yakin")
                self.progress_window_start = now
                self.progress_window_pos = (self.x, self.y)
                return
            if moved < 0.55 or (now - self.last_target_change > 22.0 and dist > self.best_dist_for_target + 0.35):
                reason = "engel yakin" if dist < 1.35 else "ilerleme yok"
                self.advance_target(reason)
                self.start_recovery()
                self.progress_window_start = now
                self.progress_window_pos = (self.x, self.y)
                return
            self.progress_window_start = now
            self.progress_window_pos = (self.x, self.y)

        speed = min(MAX_SPEED, POS_GAIN * dist)
        vx_world = speed * dx / (dist + 1e-6)
        vy_world = speed * dy / (dist + 1e-6)
        cy = math.cos(self.yaw)
        sy = math.sin(self.yaw)

        cmd = Twist()
        cmd.linear.x = self.clamp(cy * vx_world + sy * vy_world, MAX_SPEED)
        cmd.linear.y = self.clamp(-sy * vx_world + cy * vy_world, MAX_SPEED)
        cmd.linear.z = self.clamp(0.35 * (self.args.altitude - self.z), 0.10)

        target_yaw = math.atan2(dy, dx)
        yaw_err = target_yaw - self.yaw
        while yaw_err > math.pi:
            yaw_err -= 2 * math.pi
        while yaw_err < -math.pi:
            yaw_err += 2 * math.pi
        cmd.angular.z = self.clamp(TURN_GAIN * yaw_err, 0.42)

        self.cmd_pub.publish(cmd)

        if self.log_counter % 20 == 0:
            self.get_logger().info(
                f"Hedef {self.idx+1}/{len(self.targets)}=({target.x:.1f},{target.y:.1f}) "
                f"konum=({self.x:.1f},{self.y:.1f}) mesafe={dist:.2f} "
                f"visited={len(self.visited)} z={self.z:.2f}"
            )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--altitude", type=float, default=1.45)
    parser.add_argument("--duration", type=float, default=0.0)
    args = parser.parse_args()

    rclpy.init()
    node = CoverageExplorer(args)
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
