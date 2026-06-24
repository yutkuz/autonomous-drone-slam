#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import PointCloud2
import struct
import math


class LidarDebug(Node):
    def __init__(self):
        super().__init__('lidar_debug')
        self.sub = self.create_subscription(
            PointCloud2, '/simple_drone/lidar3d/points', self.callback, 10
        )
        self.count = 0

    def callback(self, msg):
        if self.count >= 3:
            rclpy.shutdown()
            return

        points = []
        data = msg.data
        point_step = msg.point_step

        for i in range(msg.width * msg.height):
            offset = i * point_step
            if offset + 12 > len(data):
                break
            x = struct.unpack_from('f', bytes(data), offset)[0]
            y = struct.unpack_from('f', bytes(data), offset + 4)[0]
            z = struct.unpack_from('f', bytes(data), offset + 8)[0]
            if math.isnan(x) or math.isnan(y) or math.isnan(z):
                continue
            points.append((x, y, z))

        # Istatistikler
        if not points:
            self.get_logger().info('Hic nokta yok!')
            self.count += 1
            return

        z_values = [p[2] for p in points]
        distances = [math.sqrt(p[0]**2 + p[1]**2) for p in points]

        self.get_logger().info(f'--- Frame {self.count} ---')
        self.get_logger().info(f'Toplam nokta: {len(points)}')
        self.get_logger().info(f'Z min: {min(z_values):.2f}, Z max: {max(z_values):.2f}, Z ort: {sum(z_values)/len(z_values):.2f}')
        self.get_logger().info(f'Mesafe min: {min(distances):.2f}, max: {max(distances):.2f}')

        # Z araligina gore dagılım
        z_bins = {}
        for p in points:
            z_bin = round(p[2], 0)
            z_bins[z_bin] = z_bins.get(z_bin, 0) + 1
        self.get_logger().info(f'Z dagilimi: {dict(sorted(z_bins.items()))}')

        # On bolge (x>0, |y|<2) en yakin 5 nokta
        front = [(x, y, z) for x, y, z in points if x > 0 and abs(y) < 2]
        front.sort(key=lambda p: p[0])
        self.get_logger().info(f'On bolge nokta sayisi: {len(front)}')
        for p in front[:5]:
            self.get_logger().info(f'  x={p[0]:.2f} y={p[1]:.2f} z={p[2]:.2f}')

        self.count += 1


def main():
    rclpy.init()
    node = LidarDebug()
    rclpy.spin(node)


if __name__ == '__main__':
    main()
