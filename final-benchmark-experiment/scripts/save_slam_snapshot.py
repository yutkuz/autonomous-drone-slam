#!/usr/bin/env python3
import argparse
import math
import os
import random
import shutil
import struct
import time
import re

import rclpy
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, HistoryPolicy, QoSProfile, ReliabilityPolicy
from sensor_msgs.msg import PointCloud2, PointField


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


class SnapshotNode(Node):
    def __init__(self, topic):
        super().__init__("final_benchmark_slam_snapshot")
        qos = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
            history=HistoryPolicy.KEEP_LAST,
            depth=1,
        )
        self.msg = None
        self.create_subscription(PointCloud2, topic, self.callback, qos)

    def callback(self, msg):
        self.msg = msg


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic", default="/cloud_map")
    default_output = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "outputs"))
    parser.add_argument("--output-root", default=default_output)
    parser.add_argument("--max-points", type=int, default=700000)
    parser.add_argument("--label", default="")
    args = parser.parse_args()

    stamp = time.strftime("%Y-%m-%d_%H-%M-%S")
    label = re.sub(r"[^A-Za-z0-9_.-]+", "_", args.label.strip())
    out_name = f"{label}_{stamp}" if label else stamp
    out_dir = os.path.join(args.output_root, out_name)
    os.makedirs(out_dir, exist_ok=True)

    rclpy.init()
    node = SnapshotNode(args.topic)
    deadline = time.time() + 15
    while rclpy.ok() and node.msg is None and time.time() < deadline:
        rclpy.spin_once(node, timeout_sec=0.2)
    if node.msg is None:
        raise SystemExit(f"{args.topic} topicinden PointCloud2 alinamadi.")

    points, raw_count = extract_points(node.msg, args.max_points)
    ply_path = os.path.join(out_dir, "cloud_map_snapshot.ply")
    png_path = os.path.join(out_dir, "cloud_map_top_preview.png")
    save_ply(ply_path, points)
    save_preview(png_path, points)

    db_src = os.path.join(os.path.expanduser("~"), ".ros", "rtabmap.db")
    db_dst = os.path.join(out_dir, "rtabmap.db")
    if os.path.exists(db_src):
        shutil.copy2(db_src, db_dst)

    with open(os.path.join(out_dir, "README.md"), "w", encoding="utf-8") as f:
        f.write("Final benchmark sjtu_drone SLAM snapshot\n")
        f.write(f"topic: {args.topic}\n")
        f.write(f"raw_points_in_message: {raw_count}\n")
        f.write(f"saved_points: {len(points)}\n")
        f.write(f"ply: {ply_path}\n")
        f.write(f"preview: {png_path}\n")
        if os.path.exists(db_dst):
            f.write(f"database: {db_dst}\n")

    print(out_dir)
    print(f"raw_points={raw_count} saved_points={len(points)}")

    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
