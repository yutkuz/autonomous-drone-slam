#!/usr/bin/env python3
# sjtu_drone odometri frame DUZELTICISI
#
# Sorun: sjtu_drone /simple_drone/odom mesajini frame_id="/simple_drone/odom"
#        (basta egik cizgi) ile yayinliyor. ROS2 tf2 bunu reddediyor:
#        "tf2 frame_ids cannot start with a '/'"
#
# Bu dugum:
#   1) /simple_drone/odom'u dinler
#   2) frame_id ve child_frame_id'deki bastaki '/' karakterini siler
#   3) Temiz mesaji /simple_drone/odom_fixed olarak yayinlar
#   4) Temiz odom->base_link TF'ini yayinlar (RViz ve RTAB-Map icin)
#
# Calistirma:
#   source ~/slam_ws/install/setup.bash
#   python3 odom_frame_fixer.py
#
# Drone zaten dogru odom->base TF'i yayinliyorsa (TF_REPEATED_DATA uyarisi
# gorursen) TF yayinini kapat:
#   python3 odom_frame_fixer.py --ros-args -p publish_tf:=false

import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from geometry_msgs.msg import TransformStamped
from tf2_ros import TransformBroadcaster


def strip_slash(frame: str) -> str:
    return frame[1:] if frame.startswith('/') else frame


class OdomFrameFixer(Node):
    def __init__(self):
        super().__init__('odom_frame_fixer')
        self.declare_parameter('publish_tf', True)
        self.publish_tf = self.get_parameter('publish_tf').value

        self.pub = self.create_publisher(Odometry, '/simple_drone/odom_fixed', 10)
        self.br = TransformBroadcaster(self)
        self.sub = self.create_subscription(
            Odometry, '/simple_drone/odom', self.cb, 10)

        self.get_logger().info(
            'odom_frame_fixer calisiyor: /simple_drone/odom -> '
            '/simple_drone/odom_fixed (publish_tf=%s)' % self.publish_tf)

    def cb(self, msg: Odometry):
        msg.header.frame_id = strip_slash(msg.header.frame_id)
        msg.child_frame_id = strip_slash(msg.child_frame_id)
        self.pub.publish(msg)

        if self.publish_tf:
            t = TransformStamped()
            t.header.stamp = msg.header.stamp          # sim saatini korur
            t.header.frame_id = msg.header.frame_id     # simple_drone/odom
            t.child_frame_id = msg.child_frame_id       # simple_drone/base_link
            t.transform.translation.x = msg.pose.pose.position.x
            t.transform.translation.y = msg.pose.pose.position.y
            t.transform.translation.z = msg.pose.pose.position.z
            t.transform.rotation = msg.pose.pose.orientation
            self.br.sendTransform(t)


def main():
    rclpy.init()
    node = OdomFrameFixer()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
