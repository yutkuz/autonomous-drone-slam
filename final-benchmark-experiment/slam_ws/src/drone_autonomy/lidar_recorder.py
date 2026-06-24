#!/usr/bin/env python3
"""
LiDAR nokta bulutunu TF kullanarak map frame'ine donusturup biriktiren node.
RTAB-Map bittiginde birlestirilmis nokta bulutunu PLY olarak kaydeder.
"""
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import PointCloud2
from nav_msgs.msg import Odometry
import struct
import math
import time
import os


class LidarRecorder(Node):
    def __init__(self):
        super().__init__('lidar_recorder', parameter_overrides=[
            rclpy.parameter.Parameter('use_sim_time', rclpy.Parameter.Type.BOOL, True)
        ])

        self.pos_x = 0.0
        self.pos_y = 0.0
        self.pos_z = 0.0
        self.qx = 0.0
        self.qy = 0.0
        self.qz = 0.0
        self.qw = 1.0

        self.all_points = []
        self.frame_count = 0
        self.save_every_n = 5  # her 5 frame'de bir kaydet (10Hz -> 2Hz)

        self.create_subscription(Odometry, '/simple_drone/odom', self.odom_cb, 10)
        self.create_subscription(PointCloud2, '/simple_drone/lidar3d/points', self.lidar_cb, 10)

        self.get_logger().info('LiDAR Recorder basladi. Ctrl+C ile durdurunca PLY kaydedecek.')

    def odom_cb(self, msg):
        self.pos_x = msg.pose.pose.position.x
        self.pos_y = msg.pose.pose.position.y
        self.pos_z = msg.pose.pose.position.z
        self.qx = msg.pose.pose.orientation.x
        self.qy = msg.pose.pose.orientation.y
        self.qz = msg.pose.pose.orientation.z
        self.qw = msg.pose.pose.orientation.w

    def quaternion_to_rotation(self, qx, qy, qz, qw):
        """Quaternion'dan 3x3 rotasyon matrisi."""
        r00 = 1 - 2*(qy*qy + qz*qz)
        r01 = 2*(qx*qy - qz*qw)
        r02 = 2*(qx*qz + qy*qw)
        r10 = 2*(qx*qy + qz*qw)
        r11 = 1 - 2*(qx*qx + qz*qz)
        r12 = 2*(qy*qz - qx*qw)
        r20 = 2*(qx*qz - qy*qw)
        r21 = 2*(qy*qz + qx*qw)
        r22 = 1 - 2*(qx*qx + qy*qy)
        return ((r00,r01,r02),(r10,r11,r12),(r20,r21,r22))

    def transform_point(self, x, y, z):
        """Noktayi drone frame'inden world frame'ine donustur."""
        # Lidar offset: 0, 0, 0.1 (base_link'e gore)
        lx, ly, lz = x, y, z + 0.1

        R = self.quaternion_to_rotation(self.qx, self.qy, self.qz, self.qw)
        wx = R[0][0]*lx + R[0][1]*ly + R[0][2]*lz + self.pos_x
        wy = R[1][0]*lx + R[1][1]*ly + R[1][2]*lz + self.pos_y
        wz = R[2][0]*lx + R[2][1]*ly + R[2][2]*lz + self.pos_z
        return wx, wy, wz

    def lidar_cb(self, msg):
        self.frame_count += 1
        if self.frame_count % self.save_every_n != 0:
            return

        data = msg.data
        point_step = msg.point_step
        num_points = msg.width * msg.height

        count = 0
        for i in range(num_points):
            offset = i * point_step
            if offset + 12 > len(data):
                break
            x = struct.unpack_from('f', bytes(data), offset)[0]
            y = struct.unpack_from('f', bytes(data), offset + 4)[0]
            z = struct.unpack_from('f', bytes(data), offset + 8)[0]

            if math.isnan(x) or math.isnan(y) or math.isnan(z):
                continue

            dist = math.sqrt(x*x + y*y + z*z)
            if dist < 0.5 or dist > 15.0:
                continue

            wx, wy, wz = self.transform_point(x, y, z)
            self.all_points.append((wx, wy, wz))
            count += 1

        if self.frame_count % 50 == 0:
            self.get_logger().info(f'Toplam {len(self.all_points)} nokta birikti ({self.frame_count} frame)')

    def save_ply(self):
        if not self.all_points:
            self.get_logger().info('Kaydedilecek nokta yok!')
            return

        output_dir = os.path.expanduser('~/slam_ws/src/drone_autonomy')
        filepath = os.path.join(output_dir, 'lidar_map.ply')

        with open(filepath, 'w') as f:
            f.write('ply\n')
            f.write('format ascii 1.0\n')
            f.write(f'element vertex {len(self.all_points)}\n')
            f.write('property float x\n')
            f.write('property float y\n')
            f.write('property float z\n')
            f.write('end_header\n')
            for p in self.all_points:
                f.write(f'{p[0]:.4f} {p[1]:.4f} {p[2]:.4f}\n')

        self.get_logger().info(f'LiDAR haritasi kaydedildi: {filepath} ({len(self.all_points)} nokta)')


def main():
    rclpy.init()
    node = LidarRecorder()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Kaydediliyor...')
        node.save_ply()
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()