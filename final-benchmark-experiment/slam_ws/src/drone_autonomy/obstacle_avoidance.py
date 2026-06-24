#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import Empty, Int8
from sensor_msgs.msg import PointCloud2
import struct
import math
import time


class ObstacleAvoidance(Node):
    def __init__(self):
        super().__init__('obstacle_avoidance')

        self.takeoff_pub = self.create_publisher(Empty, '/simple_drone/takeoff', 10)
        self.land_pub = self.create_publisher(Empty, '/simple_drone/land', 10)
        self.cmd_vel_pub = self.create_publisher(Twist, '/simple_drone/cmd_vel', 10)

        self.drone_state = 0
        self.is_flying = False
        self.min_front_dist = 999.0
        self.min_left_dist = 999.0
        self.min_right_dist = 999.0

        # Parametreler
        self.safe_distance = 2.0
        self.forward_speed = 0.3
        self.turn_speed = 0.5
        self.min_point_distance = 0.5
        self.max_point_distance = 8.0
        self.z_min = -0.3
        self.z_max = 1.0

        # Salinım onleme - donus taahhut sistemi
        self.turn_commitment = 0        # kalan donus adimi (10Hz'de kac tick)
        self.turn_direction = 0.0       # taahhut edilen yon (+1 sol, -1 sag)
        self.min_turn_ticks = 15        # en az 1.5 saniye ayni yone don

        self.state_sub = self.create_subscription(
            Int8, '/simple_drone/state', self.state_callback, 10
        )
        self.lidar_sub = self.create_subscription(
            PointCloud2, '/simple_drone/lidar3d/points', self.lidar_callback, 10
        )

        self.control_timer = self.create_timer(0.1, self.control_loop)
        self.create_timer(2.0, self.do_takeoff)
        self.takeoff_done = False
        self.log_counter = 0

        self.get_logger().info('Obstacle Avoidance v2 basladi.')

    def state_callback(self, msg):
        self.drone_state = msg.data

    def do_takeoff(self):
        if self.takeoff_done:
            return
        self.takeoff_done = True
        self.get_logger().info('Takeoff komutu gonderiliyor...')
        for _ in range(5):
            self.takeoff_pub.publish(Empty())
            time.sleep(0.1)
        time.sleep(4.0)
        self.is_flying = True
        self.get_logger().info('Drone havada! Otonom ucus basliyor.')

    def lidar_callback(self, msg):
        points = self.parse_pointcloud2(msg)

        front_dists = []
        left_dists = []
        right_dists = []
        back_dists = []

        for x, y, z in points:
            if z < self.z_min or z > self.z_max:
                continue

            dist = math.sqrt(x * x + y * y)
            if dist < self.min_point_distance or dist > self.max_point_distance:
                continue

            angle_deg = math.degrees(math.atan2(y, x))

            if -30 <= angle_deg <= 30:
                front_dists.append(dist)
            elif 30 < angle_deg <= 90:
                left_dists.append(dist)
            elif -90 <= angle_deg < -30:
                right_dists.append(dist)
            elif abs(angle_deg) > 150:
                back_dists.append(dist)

        self.min_front_dist = min(front_dists) if front_dists else 999.0
        self.min_left_dist = min(left_dists) if left_dists else 999.0
        self.min_right_dist = min(right_dists) if right_dists else 999.0
        self.min_back_dist = min(back_dists) if back_dists else 999.0

    def parse_pointcloud2(self, msg):
        points = []
        data = msg.data
        point_step = msg.point_step
        num_points = msg.width * msg.height

        for i in range(num_points):
            offset = i * point_step
            if offset + 12 > len(data):
                break
            x = struct.unpack_from('f', bytes(data), offset)[0]
            y = struct.unpack_from('f', bytes(data), offset + 4)[0]
            z = struct.unpack_from('f', bytes(data), offset + 8)[0]

            if math.isnan(x) or math.isnan(y) or math.isnan(z):
                continue
            points.append((x, y, z))

        return points

    def control_loop(self):
        if not self.is_flying:
            return

        twist = Twist()
        self.log_counter += 1
        should_log = (self.log_counter % 10 == 0)

        front_clear = self.min_front_dist > self.safe_distance
        left_clear = self.min_left_dist > (self.safe_distance * 0.7)
        right_clear = self.min_right_dist > (self.safe_distance * 0.7)

        # Aktif donus taahhudu varsa, tamamla
        if self.turn_commitment > 0:
            twist.linear.x = 0.0
            twist.angular.z = self.turn_direction * self.turn_speed

            # Eger donus sirasinda on acildiysa erken bitir
            if front_clear and self.turn_commitment < self.min_turn_ticks - 5:
                self.turn_commitment = 0
                if should_log:
                    self.get_logger().info('Donus tamamlandi (on acildi)')
            else:
                self.turn_commitment -= 1
                if should_log:
                    self.get_logger().info(
                        f'Donuyor (kalan: {self.turn_commitment}) | '
                        f'On: {self.min_front_dist:.1f}m  Sol: {self.min_left_dist:.1f}m  Sag: {self.min_right_dist:.1f}m'
                    )

        elif front_clear:
            # On acik - ileri git
            twist.linear.x = self.forward_speed
            twist.angular.z = 0.0
            if should_log:
                self.get_logger().info(
                    f'Ileri gidiyor | On: {self.min_front_dist:.1f}m  Sol: {self.min_left_dist:.1f}m  Sag: {self.min_right_dist:.1f}m'
                )

        else:
            # On kapali - donus yonunu sec ve taahhut et
            if not left_clear and not right_clear:
                # Her yer kapali - 180 derece don (uzun taahhut)
                self.turn_commitment = 30  # 3 saniye
                self.turn_direction = 1.0  # sola
                twist.linear.x = -0.1
                twist.angular.z = self.turn_speed
                if should_log:
                    self.get_logger().info(
                        f'SIKISTI! 180 derece donuyor | '
                        f'On: {self.min_front_dist:.1f}m  Sol: {self.min_left_dist:.1f}m  Sag: {self.min_right_dist:.1f}m'
                    )
            else:
                # Acik tarafa don ve taahhut et
                if right_clear and (not left_clear or self.min_right_dist >= self.min_left_dist):
                    self.turn_direction = -1.0  # saga
                    direction_str = "SAGA"
                else:
                    self.turn_direction = 1.0   # sola
                    direction_str = "SOLA"

                self.turn_commitment = self.min_turn_ticks  # 1.5 saniye

                twist.linear.x = 0.0
                twist.angular.z = self.turn_direction * self.turn_speed
                if should_log:
                    self.get_logger().info(
                        f'ENGEL! {direction_str} donuyor | '
                        f'On: {self.min_front_dist:.1f}m  Sol: {self.min_left_dist:.1f}m  Sag: {self.min_right_dist:.1f}m'
                    )

        self.cmd_vel_pub.publish(twist)

    def shutdown(self):
        self.get_logger().info('Inis yapiliyor...')
        stop = Twist()
        for _ in range(30):
            self.cmd_vel_pub.publish(stop)
            time.sleep(0.05)
        for _ in range(5):
            self.land_pub.publish(Empty())
            time.sleep(0.1)
        for _ in range(30):
            self.cmd_vel_pub.publish(stop)
            time.sleep(0.05)
        self.get_logger().info('Inis tamamlandi.')


def main():
    rclpy.init()
    node = ObstacleAvoidance()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Ctrl+C algilandi!')
        node.shutdown()
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()