#!/usr/bin/env python3
import argparse
import math
import os
import time
from collections import defaultdict, deque

import rclpy
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from sensor_msgs.msg import PointCloud2
from std_msgs.msg import Empty

try:
    from sensor_msgs_py import point_cloud2
except Exception:
    point_cloud2 = None


MAX_SPEED = 0.28
CAUTIOUS_SPEED = 0.12
GRID = 0.65
ALTITUDE_GAIN = 0.35
TURN_GAIN = 0.9
MAX_RANGE = 8.0
SECTOR_DEG = 10
STUCK_PROGRESS = 0.35
RECOVERY_PROGRESS = 0.20


def clamp(v, limit):
    return max(-limit, min(limit, v))


def norm_angle(a):
    while a > math.pi:
        a -= 2.0 * math.pi
    while a < -math.pi:
        a += 2.0 * math.pi
    return a


def angle_key(angle):
    deg = math.degrees(norm_angle(angle))
    return int(round(deg / SECTOR_DEG) * SECTOR_DEG)


class GeneralAutonomousExplorer(Node):
    """Map-agnostic local frontier explorer.

    The controller intentionally avoids hard-coded map bounds, center-obstacle
    masks, or waypoint lists. It expands a dynamic visited grid and chooses a
    motion heading from local LiDAR/depth clearance plus novelty score.
    """

    def __init__(self, args):
        super().__init__("final_benchmark_general_explorer", parameter_overrides=[
            rclpy.parameter.Parameter("use_sim_time", rclpy.Parameter.Type.BOOL, True)
        ])
        self.args = args
        self.takeoff_pub = self.create_publisher(Empty, "/simple_drone/takeoff", 10)
        self.cmd_pub = self.create_publisher(Twist, "/simple_drone/cmd_vel", 10)
        self.create_subscription(Odometry, "/simple_drone/odom", self.odom_cb, 10)
        self.create_subscription(PointCloud2, "/final_benchmark/merged_scan_cloud", self.cloud_cb, 2)

        self.x = self.y = self.z = self.yaw = 0.0
        self.start_x = self.start_y = 0.0
        self.start_time = time.monotonic()
        self.last_takeoff = 0.0
        self.flying = False
        self.done = False

        self.visited = defaultdict(int)
        self.path = deque(maxlen=180)
        self.recent_cells = deque(maxlen=60)
        self.current_heading = 0.0
        self.last_decision = 0.0

        self.sector_clear = {d: MAX_RANGE for d in range(-180, 181, SECTOR_DEG)}
        self.front_clear = MAX_RANGE
        self.left_clear = MAX_RANGE
        self.right_clear = MAX_RANGE
        self.min_clear = MAX_RANGE
        self.last_cloud = 0.0

        self.progress_time = time.monotonic()
        self.progress_pos = (0.0, 0.0)
        self.recovery_until = 0.0
        self.recovery_heading = 0.0
        self.recovery_started = (0.0, 0.0)
        self.recovery_phase = 0
        self.recovery_phase_until = 0.0
        self.recovery_last_check = 0.0
        self.recovery_side = 1.0
        self.recovery_count = 0
        self.failed_headings = deque(maxlen=28)
        self.log_counter = 0
        self.bounds = self.read_bounds()

        self.timer = self.create_timer(0.1, self.loop)
        self.get_logger().info(
            "Final benchmark autonomous explorer started: fixed map bounds, "
            "merkez engel ve waypoint yok; dinamik grid + lidar frontier aktif."
        )
        if self.bounds:
            self.get_logger().info(f"World-derived geofence aktif: {self.bounds}")

    def read_bounds(self):
        raw = os.environ.get("FINAL_BOUNDS", "").strip()
        if not raw:
            return None
        try:
            xmin, xmax, ymin, ymax = [float(v) for v in raw.split()]
        except ValueError:
            return None
        if xmin >= xmax or ymin >= ymax:
            return None
        return xmin, xmax, ymin, ymax

    def inside_bounds(self, x=None, y=None, margin=0.0):
        if not self.bounds:
            return True
        x = self.x if x is None else x
        y = self.y if y is None else y
        xmin, xmax, ymin, ymax = self.bounds
        return xmin + margin <= x <= xmax - margin and ymin + margin <= y <= ymax - margin

    def bounds_center_heading(self):
        if not self.bounds:
            return None
        xmin, xmax, ymin, ymax = self.bounds
        return math.atan2(((ymin + ymax) * 0.5) - self.y, ((xmin + xmax) * 0.5) - self.x)

    def bounds_score(self, heading):
        if not self.bounds:
            return 0.0
        score = 0.0
        xmin, xmax, ymin, ymax = self.bounds
        center_heading = self.bounds_center_heading()
        for i, step in enumerate((0.8, 1.6, 2.8, 4.2)):
            px = self.x + math.cos(heading) * step
            py = self.y + math.sin(heading) * step
            if not self.inside_bounds(px, py, margin=0.25):
                score -= 90.0 / (i + 1)
            elif not self.inside_bounds(px, py, margin=1.2):
                score -= 10.0 / (i + 1)
        if not self.inside_bounds(margin=0.4) and center_heading is not None:
            score += 35.0 * math.cos(norm_angle(heading - center_heading))
        return score

    def odom_cb(self, msg):
        self.x = msg.pose.pose.position.x
        self.y = msg.pose.pose.position.y
        self.z = msg.pose.pose.position.z
        q = msg.pose.pose.orientation
        self.yaw = math.atan2(
            2 * (q.w * q.z + q.x * q.y),
            1 - 2 * (q.y * q.y + q.z * q.z),
        )

    def cloud_cb(self, msg):
        if point_cloud2 is None:
            return
        try:
            pts = point_cloud2.read_points(msg, field_names=("x", "y", "z"), skip_nans=True)
        except Exception:
            return

        sectors = {d: MAX_RANGE for d in range(-180, 181, SECTOR_DEG)}
        front = left = right = near = MAX_RANGE
        count = 0
        for p in pts:
            x, y, z = float(p[0]), float(p[1]), float(p[2])
            if z < -0.35 or z > 1.35:
                continue
            d = math.hypot(x, y)
            if d < 0.85 or d > MAX_RANGE:
                continue
            ang = math.atan2(y, x)
            key = angle_key(ang)
            sectors[key] = min(sectors.get(key, MAX_RANGE), d)
            near = min(near, d)
            if abs(ang) < math.radians(28):
                front = min(front, d)
            elif math.radians(35) < ang < math.radians(120):
                left = min(left, d)
            elif math.radians(-120) < ang < math.radians(-35):
                right = min(right, d)
            count += 1
            if count > 6500:
                break

        self.sector_clear = sectors
        self.front_clear = front
        self.left_clear = left
        self.right_clear = right
        self.min_clear = near
        self.last_cloud = time.monotonic()

    def grid_key(self, x=None, y=None):
        x = self.x if x is None else x
        y = self.y if y is None else y
        return (round(x / GRID), round(y / GRID))

    def mark_visited(self):
        key = self.grid_key()
        self.visited[key] += 1
        if not self.recent_cells or self.recent_cells[-1] != key:
            self.recent_cells.append(key)
        if self.log_counter % 4 == 0:
            self.path.append((self.x, self.y))

    def local_clearance(self, global_heading):
        rel = norm_angle(global_heading - self.yaw)
        key = angle_key(rel)
        nearby = [key - SECTOR_DEG, key, key + SECTOR_DEG]
        return min(self.sector_clear.get(k, MAX_RANGE) for k in nearby)

    def novelty_score(self, heading):
        score = 0.0
        for i, step in enumerate((0.8, 1.4, 2.1, 3.0, 4.0)):
            px = self.x + math.cos(heading) * step
            py = self.y + math.sin(heading) * step
            key = self.grid_key(px, py)
            visits = self.visited.get(key, 0)
            score += (14.0 / (1.0 + visits)) * (1.2 / (i + 1))
            if key in self.recent_cells:
                score -= 3.0 / (i + 1)

        projected_x = self.x + math.cos(heading) * 2.2
        projected_y = self.y + math.sin(heading) * 2.2
        for px, py in list(self.path)[-35:]:
            d = math.hypot(projected_x - px, projected_y - py)
            if d < 0.75:
                score -= 2.2
            elif d < 1.4:
                score -= 0.6
        return score

    def failed_heading_penalty(self, heading):
        now = time.monotonic()
        penalty = 0.0
        kept = deque(maxlen=self.failed_headings.maxlen)
        for fx, fy, fh, expiry in self.failed_headings:
            if expiry < now:
                continue
            kept.append((fx, fy, fh, expiry))
            pos_d = math.hypot(self.x - fx, self.y - fy)
            ang_d = abs(norm_angle(heading - fh))
            if pos_d < 2.2 and ang_d < math.radians(38):
                penalty += 55.0 * (1.0 - pos_d / 2.2) * (1.0 - ang_d / math.radians(38))
        self.failed_headings = kept
        return penalty

    def expansion_score(self, heading):
        # Mildly prefer moving away from the local centroid of recent motion.
        if len(self.path) < 8:
            return 0.0
        recent = list(self.path)[-40:]
        cx = sum(p[0] for p in recent) / len(recent)
        cy = sum(p[1] for p in recent) / len(recent)
        away = math.atan2(self.y - cy, self.x - cx)
        from_start = math.atan2(self.y - self.start_y, self.x - self.start_x)
        return 2.0 * math.cos(norm_angle(heading - away)) + 0.8 * math.cos(norm_angle(heading - from_start))

    def heading_score(self, heading):
        clearance = self.local_clearance(heading)
        score = self.novelty_score(heading)
        score += self.expansion_score(heading)
        score += self.bounds_score(heading)
        score -= self.failed_heading_penalty(heading)
        score += 1.8 * math.cos(norm_angle(heading - self.current_heading))

        if clearance < 0.95:
            score -= 120.0
        elif clearance < 1.35:
            score -= 35.0
        elif clearance < 2.0:
            score -= 8.0
        else:
            score += min(clearance, 5.0) * 1.5

        # Keep a corridor bias only when the direction is actually open.
        rel = abs(norm_angle(heading - self.yaw))
        if rel < math.radians(30) and self.front_clear > 2.0:
            score += 2.5
        return score

    def candidate_headings(self):
        headings = []
        for deg in range(-180, 181, 20):
            headings.append(norm_angle(self.yaw + math.radians(deg)))
        for deg in (0, 45, 90, 135, 180, -135, -90, -45):
            headings.append(math.radians(deg))
        headings.append(self.current_heading)
        return headings

    def choose_heading(self):
        candidates = self.candidate_headings()
        return max(candidates, key=self.heading_score)

    def choose_escape_heading(self):
        candidates = [norm_angle(self.yaw + math.radians(deg)) for deg in range(-180, 181, 15)]
        if self.bounds:
            center_heading = self.bounds_center_heading()
            if center_heading is not None:
                candidates.extend([
                    center_heading,
                    norm_angle(center_heading + math.radians(35)),
                    norm_angle(center_heading - math.radians(35)),
                ])
        candidates.extend([
            norm_angle(self.current_heading + math.pi),
            norm_angle(self.current_heading + math.pi * 0.5),
            norm_angle(self.current_heading - math.pi * 0.5),
        ])

        def score(h):
            clearance = self.local_clearance(h)
            if clearance < 0.85:
                return -999.0
            return (
                clearance * 4.0
                + 0.35 * self.novelty_score(h)
                + self.bounds_score(h)
                - self.failed_heading_penalty(h)
                - 1.5 * math.cos(norm_angle(h - self.current_heading))
            )

        return max(candidates, key=score)

    def start_recovery(self, reason):
        now = time.monotonic()
        self.recovery_count += 1
        self.recovery_until = now + min(7.5, 3.8 + 0.7 * self.recovery_count)
        self.recovery_heading = self.choose_escape_heading()
        self.recovery_started = (self.x, self.y)
        self.recovery_phase = 0
        self.recovery_phase_until = now + 1.2
        self.recovery_last_check = now
        self.recovery_side = 1.0 if self.left_clear >= self.right_clear else -1.0
        self.get_logger().warn(
            f"Recovery: {reason}. escape={math.degrees(self.recovery_heading):.0f} "
            f"clear={self.local_clearance(self.recovery_heading):.1f}"
        )

    def publish_world_velocity(self, heading, speed, yaw_target=None, z_limit=0.10):
        cmd = Twist()
        cmd.linear.z = clamp(ALTITUDE_GAIN * (self.args.altitude - self.z), z_limit)
        vx_w = speed * math.cos(heading)
        vy_w = speed * math.sin(heading)
        cy = math.cos(self.yaw)
        sy = math.sin(self.yaw)
        cmd.linear.x = clamp(cy * vx_w + sy * vy_w, MAX_SPEED)
        cmd.linear.y = clamp(-sy * vx_w + cy * vy_w, MAX_SPEED)
        target = heading if yaw_target is None else yaw_target
        cmd.angular.z = clamp(TURN_GAIN * norm_angle(target - self.yaw), 0.55)
        self.cmd_pub.publish(cmd)

    def run_recovery(self, now):
        total_moved = math.hypot(self.x - self.recovery_started[0], self.y - self.recovery_started[1])

        if now - self.recovery_last_check > 1.3:
            if total_moved < RECOVERY_PROGRESS:
                self.failed_headings.append((self.x, self.y, self.recovery_heading, now + 28.0))
                self.recovery_heading = self.choose_escape_heading()
                self.recovery_side *= -1.0
                self.recovery_phase = min(2, self.recovery_phase + 1)
                self.recovery_phase_until = now + 1.3
                self.get_logger().warn(
                    f"Recovery yon degisti: escape={math.degrees(self.recovery_heading):.0f} "
                    f"clear={self.local_clearance(self.recovery_heading):.1f}"
                )
            self.recovery_last_check = now

        if now > self.recovery_phase_until and self.recovery_phase < 2:
            self.recovery_phase += 1
            self.recovery_phase_until = now + 1.4

        if self.recovery_phase == 0:
            # Back away from the failed travel direction before trying a new frontier.
            back_heading = norm_angle(self.current_heading + math.pi)
            self.publish_world_velocity(back_heading, CAUTIOUS_SPEED, yaw_target=self.recovery_heading)
        elif self.recovery_phase == 1:
            side_heading = norm_angle(self.recovery_heading + self.recovery_side * math.pi * 0.5)
            side_clear = self.local_clearance(side_heading)
            if side_clear < 1.0:
                self.recovery_side *= -1.0
                side_heading = norm_angle(self.recovery_heading + self.recovery_side * math.pi * 0.5)
            self.publish_world_velocity(side_heading, CAUTIOUS_SPEED, yaw_target=self.recovery_heading)
        else:
            clearance = self.local_clearance(self.recovery_heading)
            speed = CAUTIOUS_SPEED if clearance < 1.8 else MAX_SPEED * 0.78
            self.publish_world_velocity(self.recovery_heading, speed)

        if total_moved > 0.55 or now > self.recovery_until:
            self.progress_time = now
            self.progress_pos = (self.x, self.y)
            self.current_heading = self.recovery_heading
            self.last_decision = 0.0
            self.recovery_until = 0.0

    def coverage_estimate(self):
        # Dynamic metric: unique visited cells vs explored bounding box.
        if not self.visited:
            return 0.0
        xs = [k[0] for k in self.visited.keys()]
        ys = [k[1] for k in self.visited.keys()]
        area = max(1, (max(xs) - min(xs) + 1) * (max(ys) - min(ys) + 1))
        return 100.0 * len(self.visited) / area

    def try_takeoff(self):
        now = time.monotonic()
        if now - self.last_takeoff > 0.6 and self.z < self.args.altitude - 0.35:
            self.takeoff_pub.publish(Empty())
            self.last_takeoff = now

    def loop(self):
        self.log_counter += 1
        now = time.monotonic()
        elapsed = now - self.start_time
        self.mark_visited()

        if self.done:
            return

        if self.args.duration > 0 and elapsed > self.args.duration:
            self.cmd_pub.publish(Twist())
            self.get_logger().info(
                f"Sure doldu. Genel explorer bitti. Dinamik grid kapsama={self.coverage_estimate():.1f}%"
            )
            self.done = True
            rclpy.try_shutdown()
            return

        self.try_takeoff()
        if not self.flying:
            cmd = Twist()
            cmd.linear.z = clamp(0.4 * (self.args.altitude - self.z), 0.15)
            self.cmd_pub.publish(cmd)
            if abs(self.args.altitude - self.z) < 0.22:
                self.flying = True
                self.start_x = self.x
                self.start_y = self.y
                self.progress_time = now
                self.progress_pos = (self.x, self.y)
                self.current_heading = self.yaw
                self.get_logger().info(f"Irtifada ({self.z:.2f}m), genel kesif basliyor.")
            return

        if now < self.recovery_until:
            self.run_recovery(now)
            return

        moved = math.hypot(self.x - self.progress_pos[0], self.y - self.progress_pos[1])
        if now - self.progress_time > 10.0:
            if not self.inside_bounds(margin=0.2):
                self.start_recovery("geofence disina cikildi")
                return
            if moved < STUCK_PROGRESS:
                self.failed_headings.append((self.x, self.y, self.current_heading, now + 24.0))
                self.start_recovery("ilerleme az")
                return
            if self.front_clear < 0.85 and self.left_clear < 1.15 and self.right_clear < 1.15:
                self.start_recovery("lokal sikisma")
                return
            self.progress_time = now
            self.progress_pos = (self.x, self.y)
            self.recovery_count = max(0, self.recovery_count - 1)

        if now - self.last_decision > 1.1:
            self.current_heading = self.choose_heading()
            self.last_decision = now

        clearance = self.local_clearance(self.current_heading)
        speed = MAX_SPEED
        if clearance < 1.5:
            speed = CAUTIOUS_SPEED
        elif clearance < 2.2:
            speed = 0.19

        cmd = Twist()
        cmd.linear.z = clamp(ALTITUDE_GAIN * (self.args.altitude - self.z), 0.10)
        vx_w = speed * math.cos(self.current_heading)
        vy_w = speed * math.sin(self.current_heading)
        cy = math.cos(self.yaw)
        sy = math.sin(self.yaw)
        cmd.linear.x = clamp(cy * vx_w + sy * vy_w, MAX_SPEED)
        cmd.linear.y = clamp(-sy * vx_w + cy * vy_w, MAX_SPEED)
        cmd.angular.z = clamp(TURN_GAIN * norm_angle(self.current_heading - self.yaw), 0.50)
        self.cmd_pub.publish(cmd)

        if self.log_counter % 20 == 0:
            self.get_logger().info(
                f"auto pos=({self.x:.1f},{self.y:.1f}) heading={math.degrees(self.current_heading):.0f} "
                f"visited={len(self.visited)} recent={len(set(self.recent_cells))} "
                f"clear F/L/R={self.front_clear:.1f}/{self.left_clear:.1f}/{self.right_clear:.1f} "
                f"dir_clear={clearance:.1f} dyn_cov={self.coverage_estimate():.1f}%"
            )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--altitude", type=float, default=1.45)
    parser.add_argument("--duration", type=float, default=0.0)
    args = parser.parse_args()

    rclpy.init()
    node = GeneralAutonomousExplorer(args)
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
