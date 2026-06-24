import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu

class ImuReader(Node):
    def __init__(self):
        super().__init__('imu_reader')
        self.subscription = self.create_subscription(
            Imu,
            #Dinlenen topic aşşağıda
            '/simple_drone/imu/out',
            self.imu_callback,
            10
        )
        self.get_logger().info('IMU Reader başlatıldı, veri bekleniyor...')

    def imu_callback(self, msg):
        self.get_logger().info(
            f'Oryantasyon → x: {msg.orientation.x:.3f} | y: {msg.orientation.y:.3f} | z: {msg.orientation.z:.3f} | w: {msg.orientation.w:.3f}\n'
            f'Açısal Hız  → x: {msg.angular_velocity.x:.3f} | y: {msg.angular_velocity.y:.3f} | z: {msg.angular_velocity.z:.3f}\n'
            f'Lineer İvme → x: {msg.linear_acceleration.x:.3f} | y: {msg.linear_acceleration.y:.3f} | z: {msg.linear_acceleration.z:.3f}\n'
        )

def main(args=None):
    rclpy.init(args=args)
    node = ImuReader()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()