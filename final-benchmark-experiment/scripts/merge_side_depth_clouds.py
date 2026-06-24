#!/usr/bin/env python3
import math
import random
import struct

import rclpy
from geometry_msgs.msg import TransformStamped
from rclpy.duration import Duration
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, QoSProfile, ReliabilityPolicy
from sensor_msgs.msg import PointCloud2, PointField
from sensor_msgs_py import point_cloud2
import tf2_ros


TARGET_FRAME = "simple_drone/base_link"


def quat_rotate(q, p):
    x, y, z = p
    qx, qy, qz, qw = q
    # v' = v + 2*w*(qvec x v) + 2*(qvec x (qvec x v))
    cx = qy * z - qz * y
    cy = qz * x - qx * z
    cz = qx * y - qy * x
    c2x = qy * cz - qz * cy
    c2y = qz * cx - qx * cz
    c2z = qx * cy - qy * cx
    return (
        x + 2.0 * (qw * cx + c2x),
        y + 2.0 * (qw * cy + c2y),
        z + 2.0 * (qw * cz + c2z),
    )


def rgb_float(r, g, b):
    i = (int(r) << 16) | (int(g) << 8) | int(b)
    return struct.unpack("f", struct.pack("I", i))[0]


class SideDepthCloudMerger(Node):
    def __init__(self):
        super().__init__("final_benchmark_side_depth_cloud_merger")
        self.tf_buffer = tf2_ros.Buffer(cache_time=Duration(seconds=10.0))
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)
        self.latest = {}

        qos = QoSProfile(depth=2)
        qos.reliability = ReliabilityPolicy.BEST_EFFORT
        qos.durability = DurabilityPolicy.VOLATILE

        self.create_subscription(PointCloud2, "/simple_drone/lidar3d/points", self._cb("lidar"), qos)
        self.create_subscription(PointCloud2, "/simple_drone/right/points", self._cb("right"), qos)
        self.create_subscription(PointCloud2, "/simple_drone/left/points", self._cb("left"), qos)

        self.pub = self.create_publisher(PointCloud2, "/final_benchmark/merged_scan_cloud", 2)
        self.timer = self.create_timer(0.8, self.publish_merged)
        self.get_logger().info("Final benchmark cloud merger active: lidar + right depth + left depth")

    def _cb(self, name):
        def cb(msg):
            self.latest[name] = msg
        return cb

    def transform_for(self, source_frame):
        try:
            return self.tf_buffer.lookup_transform(
                TARGET_FRAME, source_frame, rclpy.time.Time(), timeout=Duration(seconds=0.05)
            )
        except Exception:
            return None

    def convert_cloud(self, name, msg, max_points):
        tf = self.transform_for(msg.header.frame_id)
        if tf is None:
            return []

        t = tf.transform.translation
        q = tf.transform.rotation
        quat = (q.x, q.y, q.z, q.w)
        trans = (t.x, t.y, t.z)

        fields = [f.name for f in msg.fields]
        use_rgb = "rgb" in fields
        read_fields = ("x", "y", "z", "rgb") if use_rgb else ("x", "y", "z")
        total = msg.width * msg.height
        stride = max(1, total // max_points)
        pts = []

        for i, p in enumerate(point_cloud2.read_points(msg, field_names=read_fields, skip_nans=True)):
            if i % stride:
                continue
            x, y, z = float(p[0]), float(p[1]), float(p[2])
            if not (math.isfinite(x) and math.isfinite(y) and math.isfinite(z)):
                continue
            bx, by, bz = quat_rotate(quat, (x, y, z))
            bx += trans[0]
            by += trans[1]
            bz += trans[2]
            if not (-0.8 <= bz <= 4.0):
                continue
            if use_rgb:
                rgb = float(p[3])
            elif name == "lidar":
                rgb = rgb_float(190, 190, 190)
            elif name == "right":
                rgb = rgb_float(70, 160, 255)
            else:
                rgb = rgb_float(255, 150, 70)
            pts.append((bx, by, bz, rgb))
        return pts

    def publish_merged(self):
        if "lidar" not in self.latest:
            return

        points = []
        points.extend(self.convert_cloud("lidar", self.latest["lidar"], 35000))
        if "right" in self.latest:
            points.extend(self.convert_cloud("right", self.latest["right"], 45000))
        if "left" in self.latest:
            points.extend(self.convert_cloud("left", self.latest["left"], 45000))

        if not points:
            return

        if len(points) > 110000:
            points = random.sample(points, 110000)

        header = self.latest["lidar"].header
        header.frame_id = TARGET_FRAME
        fields = [
            PointField(name="x", offset=0, datatype=PointField.FLOAT32, count=1),
            PointField(name="y", offset=4, datatype=PointField.FLOAT32, count=1),
            PointField(name="z", offset=8, datatype=PointField.FLOAT32, count=1),
            PointField(name="rgb", offset=12, datatype=PointField.FLOAT32, count=1),
        ]
        self.pub.publish(point_cloud2.create_cloud(header, fields, points))


def main():
    rclpy.init()
    node = SideDepthCloudMerger()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
