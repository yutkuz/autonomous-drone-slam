#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy
from sensor_msgs.msg import CameraInfo, Image


CAMERAS = {
    "front": "simple_drone/front_cam_optical",
    "right": "simple_drone/right_cam_optical",
    "left": "simple_drone/left_cam_optical",
}

PUB_QOS = QoSProfile(depth=10)
PUB_QOS.reliability = ReliabilityPolicy.RELIABLE

SUB_QOS = QoSProfile(depth=10)
SUB_QOS.reliability = ReliabilityPolicy.RELIABLE


class MultiCameraFrameFixer(Node):
    def __init__(self):
        super().__init__("final_benchmark_multi_camera_frame_fixer")
        self.pubs = {}

        for name, optical_frame in CAMERAS.items():
            self.pubs[name] = {
                "rgb": self.create_publisher(
                    Image, f"/simple_drone/{name}/image_optical", PUB_QOS),
                "depth": self.create_publisher(
                    Image, f"/simple_drone/{name}/depth/image_optical", PUB_QOS),
                "info": self.create_publisher(
                    CameraInfo, f"/simple_drone/{name}/camera_info_optical", PUB_QOS),
                "frame": optical_frame,
            }
            self.create_subscription(
                Image,
                f"/simple_drone/{name}/image_raw",
                self._make_image_cb(name, "rgb"),
                SUB_QOS,
            )
            self.create_subscription(
                Image,
                f"/simple_drone/{name}/depth/image_raw",
                self._make_image_cb(name, "depth"),
                SUB_QOS,
            )
            self.create_subscription(
                CameraInfo,
                f"/simple_drone/{name}/camera_info",
                self._make_info_cb(name),
                SUB_QOS,
            )

        self.get_logger().info(
            "Final benchmark multi-camera frame fixer active: front + right + left")

    def _make_image_cb(self, camera_name, key):
        def cb(msg):
            msg.header.frame_id = self.pubs[camera_name]["frame"]
            self.pubs[camera_name][key].publish(msg)
        return cb

    def _make_info_cb(self, camera_name):
        def cb(msg):
            msg.header.frame_id = self.pubs[camera_name]["frame"]
            self.pubs[camera_name]["info"].publish(msg)
        return cb


def main():
    rclpy.init()
    node = MultiCameraFrameFixer()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
