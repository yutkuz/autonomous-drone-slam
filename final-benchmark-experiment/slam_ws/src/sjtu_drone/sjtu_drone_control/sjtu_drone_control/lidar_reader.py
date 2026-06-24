import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan

class LidarReader(Node):
    def __init__(self):
        super().__init__('lidar_reader')
        self.subscription = self.create_subscription(
            LaserScan,
            '/simple_drone/lidar/scan',
            self.lidar_callback,
            10
        )
        self.get_logger().info('LiDAR Reader baslatildi, veri bekleniyor...')

    def lidar_callback(self, msg):
        # 360 adet mesafe degeri gelir, her biri bir açıya karsilık gelir
        ranges = msg.ranges

        # Sonsuz ve gecersiz degerleri filtrele
        gecerli = [r for r in ranges if r != float('inf') and r > msg.range_min]

        if gecerli:
            en_yakin = min(gecerli)
            en_uzak  = max(gecerli)
            ortalama = sum(gecerli) / len(gecerli)

            self.get_logger().info(
                f'Toplam ölçüm: {len(ranges)} | '
                f'Geçerli: {len(gecerli)} | '
                f'En yakın engel: {en_yakin:.2f}m | '
                f'En uzak: {en_uzak:.2f}m | '
                f'Ortalama: {ortalama:.2f}m'
            )
        else:
            self.get_logger().info('Menzil içinde engel yok.')

def main(args=None):
    rclpy.init(args=args)
    node = LidarReader()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()