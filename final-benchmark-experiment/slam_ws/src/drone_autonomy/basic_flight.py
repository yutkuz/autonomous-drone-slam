#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import Empty, Int8
import time


class BasicFlight(Node):
    def __init__(self):
        super().__init__('basic_flight')

        # Publisher'lar
        self.takeoff_pub = self.create_publisher(Empty, '/simple_drone/takeoff', 10)
        self.land_pub = self.create_publisher(Empty, '/simple_drone/land', 10)
        self.cmd_vel_pub = self.create_publisher(Twist, '/simple_drone/cmd_vel', 10)

        # Drone state takibi
        self.drone_state = 0
        self.state_sub = self.create_subscription(
            Int8, '/simple_drone/state', self.state_callback, 10
        )

        # 2 saniye sonra uçuşu başlat (publisher'ların bağlanması için bekle)
        self.create_timer(2.0, self.start_mission)
        self.mission_started = False

    def state_callback(self, msg):
        self.drone_state = msg.data

    def start_mission(self):
        if self.mission_started:
            return
        self.mission_started = True

        self.get_logger().info('=== MISSION BASLIYOR ===')

        # 1) Takeoff
        self.get_logger().info('Takeoff komutu gonderiliyor...')
        for _ in range(5):
            self.takeoff_pub.publish(Empty())
            time.sleep(0.1)

        self.get_logger().info('Yukselme icin 4 saniye bekleniyor...')
        time.sleep(4.0)

        # 2) Ileri git (linear.x = 0.3 m/s, 3 saniye)
        self.get_logger().info('Ileri gidiliyor (0.3 m/s, 3 saniye)...')
        twist = Twist()
        twist.linear.x = 0.3
        start = time.time()
        while time.time() - start < 3.0:
            self.cmd_vel_pub.publish(twist)
            time.sleep(0.1)

        # 3) Dur
        self.get_logger().info('Duruyor...')
        stop_twist = Twist()
        for _ in range(10):
            self.cmd_vel_pub.publish(stop_twist)
            time.sleep(0.1)

        time.sleep(2.0)

        # 4) Land
        self.get_logger().info('Inis komutu gonderiliyor...')
        for _ in range(5):
            self.land_pub.publish(Empty())
            time.sleep(0.1)

        self.get_logger().info('=== MISSION TAMAMLANDI ===')

        # Node'u kapat
        time.sleep(2.0)
        rclpy.shutdown()


def main():
    rclpy.init()
    node = BasicFlight()
    rclpy.spin(node)


if __name__ == '__main__':
    main()
