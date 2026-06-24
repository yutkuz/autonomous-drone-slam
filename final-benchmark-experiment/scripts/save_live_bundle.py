#!/usr/bin/env python3
import argparse
import math
import os
import random
import shutil
import struct
import time

import numpy as np
import rclpy
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, QoSProfile, ReliabilityPolicy
from sensor_msgs.msg import Image, PointCloud2, PointField


def field_map(msg):
    return {field.name: field for field in msg.fields}


def unpack_value(data, offset, datatype, endian):
    formats = {
        PointField.INT8: "b",
        PointField.UINT8: "B",
        PointField.INT16: "h",
        PointField.UINT16: "H",
        PointField.INT32: "i",
        PointField.UINT32: "I",
        PointField.FLOAT32: "f",
        PointField.FLOAT64: "d",
    }
    return struct.unpack_from(endian + formats[datatype], data, offset)[0]


def rgb_from_float(value):
    packed = struct.pack("f", float(value))
    integer = struct.unpack("I", packed)[0]
    return (integer >> 16) & 255, (integer >> 8) & 255, integer & 255


def extract_points(msg, max_points):
    fields = field_map(msg)
    endian = ">" if msg.is_bigendian else "<"
    rgb_field = fields.get("rgb", fields.get("rgba"))
    total = msg.width * msg.height
    stride = max(1, total // max_points) if max_points > 0 else 1
    points = []
    for index in range(0, total, stride):
        base = index * msg.point_step
        try:
            x = float(unpack_value(msg.data, base + fields["x"].offset, fields["x"].datatype, endian))
            y = float(unpack_value(msg.data, base + fields["y"].offset, fields["y"].datatype, endian))
            z = float(unpack_value(msg.data, base + fields["z"].offset, fields["z"].datatype, endian))
        except Exception:
            continue
        if not (math.isfinite(x) and math.isfinite(y) and math.isfinite(z)):
            continue
        r, g, b = 180, 180, 180
        if rgb_field is not None:
            raw = unpack_value(msg.data, base + rgb_field.offset, rgb_field.datatype, endian)
            if rgb_field.datatype == PointField.FLOAT32:
                r, g, b = rgb_from_float(raw)
            else:
                raw = int(raw)
                r, g, b = (raw >> 16) & 255, (raw >> 8) & 255, raw & 255
        points.append((x, y, z, r, g, b))
    return points, total


def save_ply(path, points):
    with open(path, "w", encoding="ascii") as f:
        f.write("ply\nformat ascii 1.0\n")
        f.write(f"element vertex {len(points)}\n")
        f.write("property float x\nproperty float y\nproperty float z\n")
        f.write("property uchar red\nproperty uchar green\nproperty uchar blue\n")
        f.write("end_header\n")
        for x, y, z, r, g, b in points:
            f.write(f"{x:.5f} {y:.5f} {z:.5f} {int(r)} {int(g)} {int(b)}\n")


def save_preview(path, points, size=1400):
    from PIL import Image, ImageDraw
    img = Image.new("RGB", (size, size), (12, 14, 18))
    if not points:
        img.save(path)
        return
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    span = max(max_x - min_x, max_y - min_y, 1e-6)
    pad = 40
    scale = (size - 2 * pad) / span
    draw = ImageDraw.Draw(img)
    sample = points if len(points) <= 600000 else random.sample(points, 600000)
    for x, y, z, r, g, b in sample:
        px = int((x - min_x) * scale + pad)
        py = int(size - ((y - min_y) * scale + pad))
        if 0 <= px < size and 0 <= py < size:
            draw.point((px, py), fill=(int(r), int(g), int(b)))
    img.save(path)


def save_rgb_png(path, msg):
    from PIL import Image
    enc = msg.encoding.lower()
    if enc not in {"rgb8", "bgr8"}:
        raise RuntimeError(f"Unsupported RGB encoding: {msg.encoding}")
    arr = np.frombuffer(msg.data, dtype=np.uint8).reshape((msg.height, msg.step))
    arr = arr[:, : msg.width * 3].reshape((msg.height, msg.width, 3))
    if enc == "bgr8":
        arr = arr[:, :, ::-1]
    Image.fromarray(arr, mode="RGB").save(path)


def save_depth_png(path, msg):
    from PIL import Image
    enc = msg.encoding.lower()
    if enc == "32fc1":
        arr = np.frombuffer(msg.data, dtype=np.float32).reshape((msg.height, msg.width))
    elif enc == "16uc1":
        arr = np.frombuffer(msg.data, dtype=np.uint16).reshape((msg.height, msg.width)).astype(np.float32)
    else:
        raise RuntimeError(f"Unsupported depth encoding: {msg.encoding}")
    arr = np.nan_to_num(arr, nan=0.0, posinf=0.0, neginf=0.0)
    valid = arr[arr > 0]
    max_v = float(np.percentile(valid, 95)) if valid.size else 1.0
    max_v = max(max_v, 1e-6)
    img = (np.clip(arr / max_v, 0.0, 1.0) * 255.0).astype(np.uint8)
    Image.fromarray(img, mode="L").save(path)


class CaptureNode(Node):
    def __init__(self):
        super().__init__("final_benchmark_live_bundle_capture")
        self.lidar = None
        self.cloud = None
        self.rgb = None
        self.depth = None
        self.right_rgb = None
        self.right_depth = None
        self.left_rgb = None
        self.left_depth = None

        live_qos = QoSProfile(depth=10)
        live_qos.reliability = ReliabilityPolicy.BEST_EFFORT
        live_qos.durability = DurabilityPolicy.VOLATILE

        map_qos = QoSProfile(depth=1)
        map_qos.reliability = ReliabilityPolicy.RELIABLE
        map_qos.durability = DurabilityPolicy.TRANSIENT_LOCAL

        self.create_subscription(PointCloud2, "/simple_drone/lidar3d/points", self.lidar_cb, live_qos)
        self.create_subscription(PointCloud2, "/cloud_map", self.cloud_cb, map_qos)
        self.create_subscription(Image, "/simple_drone/front/image_raw", self.rgb_cb, live_qos)
        self.create_subscription(Image, "/simple_drone/front/depth/image_raw", self.depth_cb, live_qos)
        self.create_subscription(Image, "/simple_drone/right/image_raw", self.right_rgb_cb, live_qos)
        self.create_subscription(Image, "/simple_drone/right/depth/image_raw", self.right_depth_cb, live_qos)
        self.create_subscription(Image, "/simple_drone/left/image_raw", self.left_rgb_cb, live_qos)
        self.create_subscription(Image, "/simple_drone/left/depth/image_raw", self.left_depth_cb, live_qos)

    def lidar_cb(self, msg):
        self.lidar = msg

    def cloud_cb(self, msg):
        self.cloud = msg

    def rgb_cb(self, msg):
        self.rgb = msg

    def depth_cb(self, msg):
        self.depth = msg

    def right_rgb_cb(self, msg):
        self.right_rgb = msg

    def right_depth_cb(self, msg):
        self.right_depth = msg

    def left_rgb_cb(self, msg):
        self.left_rgb = msg

    def left_depth_cb(self, msg):
        self.left_depth = msg


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--max-points", type=int, default=700000)
    parser.add_argument("--timeout", type=float, default=30.0)
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)
    rclpy.init()
    node = CaptureNode()
    deadline = time.time() + args.timeout
    while rclpy.ok() and time.time() < deadline:
        rclpy.spin_once(node, timeout_sec=0.2)
        if node.lidar and node.cloud and node.rgb and node.depth:
            break

    missing = []
    if node.lidar is None:
        missing.append("lidar")
    if node.cloud is None:
        missing.append("cloud_map")
    if node.rgb is None:
        missing.append("rgb")
    if node.depth is None:
        missing.append("depth")
    if missing:
        raise SystemExit("Eksik topic: " + ", ".join(missing))

    lidar_dir = os.path.join(args.output_dir, "lidar")
    camera_dir = os.path.join(args.output_dir, "camera")
    fused_dir = os.path.join(args.output_dir, "fused_slam")
    os.makedirs(lidar_dir, exist_ok=True)
    os.makedirs(camera_dir, exist_ok=True)
    os.makedirs(fused_dir, exist_ok=True)

    lidar_points, lidar_raw = extract_points(node.lidar, args.max_points)
    cloud_points, cloud_raw = extract_points(node.cloud, args.max_points)

    save_ply(os.path.join(lidar_dir, "lidar_points.ply"), lidar_points)
    save_preview(os.path.join(lidar_dir, "lidar_top_preview.png"), lidar_points)
    save_rgb_png(os.path.join(camera_dir, "front_rgb.png"), node.rgb)
    save_depth_png(os.path.join(camera_dir, "front_depth.png"), node.depth)
    if node.right_rgb is not None:
        save_rgb_png(os.path.join(camera_dir, "right_rgb.png"), node.right_rgb)
    if node.right_depth is not None:
        save_depth_png(os.path.join(camera_dir, "right_depth.png"), node.right_depth)
    if node.left_rgb is not None:
        save_rgb_png(os.path.join(camera_dir, "left_rgb.png"), node.left_rgb)
    if node.left_depth is not None:
        save_depth_png(os.path.join(camera_dir, "left_depth.png"), node.left_depth)
    save_ply(os.path.join(fused_dir, "cloud_map_snapshot.ply"), cloud_points)
    save_preview(os.path.join(fused_dir, "cloud_map_top_preview.png"), cloud_points)

    db_src = os.path.expanduser("~/Desktop/Project-Final/final-benchmark-experiment/outputs/rtabmap.db")
    if os.path.exists(db_src):
        shutil.copy2(db_src, os.path.join(fused_dir, "rtabmap_live.db"))

    with open(os.path.join(args.output_dir, "README.md"), "w", encoding="utf-8") as f:
        f.write("Final benchmark live snapshot\n")
        f.write("lidar/lidar_points.ply\n")
        f.write("lidar/lidar_top_preview.png\n")
        f.write("camera/front_rgb.png\n")
        f.write("camera/front_depth.png\n")
        f.write("camera/right_rgb.png\n")
        f.write("camera/right_depth.png\n")
        f.write("camera/left_rgb.png\n")
        f.write("camera/left_depth.png\n")
        f.write("fused_slam/cloud_map_snapshot.ply\n")
        f.write("fused_slam/cloud_map_top_preview.png\n")
        f.write(f"lidar_raw_points: {lidar_raw}\n")
        f.write(f"cloud_raw_points: {cloud_raw}\n")

    print(args.output_dir)
    print(f"lidar_raw={lidar_raw} cloud_raw={cloud_raw}")

    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
