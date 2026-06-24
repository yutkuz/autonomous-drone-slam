#!/usr/bin/env python3
import math
import sys
import xml.etree.ElementTree as ET


def values(text, count, default=0.0):
    parts = [] if text is None else text.split()
    out = []
    for i in range(count):
        try:
            out.append(float(parts[i]))
        except (IndexError, ValueError):
            out.append(default)
    return out


def combined_pose(*poses):
    x = y = z = yaw = 0.0
    for pose in poses:
        px, py, pz, _, _, pyaw = values(pose, 6)
        cy = math.cos(yaw)
        sy = math.sin(yaw)
        x += cy * px - sy * py
        y += sy * px + cy * py
        z += pz
        yaw += pyaw
    return x, y, z, yaw


def extract_profile(root):
    floors = []

    for model in root.findall(".//model"):
        if model.findtext("static", "false").strip().lower() != "true":
            continue
        model_pose = model.findtext("pose", "0 0 0 0 0 0")
        for link in model.findall("link"):
            link_pose = link.findtext("pose", "0 0 0 0 0 0")
            for geom_parent in list(link.findall("collision")) + list(link.findall("visual")):
                size_text = geom_parent.findtext("geometry/box/size")
                if not size_text:
                    continue
                sx, sy, sz = values(size_text, 3)
                if sx < 1.5 or sy < 1.5 or sz > 0.25:
                    continue
                gx, gy, gz, _ = combined_pose(model_pose, link_pose, geom_parent.findtext("pose", "0 0 0 0 0 0"))
                if abs(gz) > 0.35:
                    continue
                name = link.get("name", "").lower()
                preferred = any(token in name for token in ("road", "asphalt", "floor", "corridor", "room", "hall", "gallery"))
                start_preferred = any(token in name for token in ("start", "entry", "spawn"))
                floors.append((gx - sx / 2.0, gx + sx / 2.0, gy - sy / 2.0, gy + sy / 2.0, sx * sy, gx, gy, preferred, start_preferred))

    if not floors:
        return {
            "has_bounds": 0,
            "spawn_x": 0.0,
            "spawn_y": 0.0,
            "spawn_yaw": 0.0,
            "bounds": "",
        }

    xmin = min(f[0] for f in floors)
    xmax = max(f[1] for f in floors)
    ymin = min(f[2] for f in floors)
    ymax = max(f[3] for f in floors)
    start_preferred = [f for f in floors if f[8]]
    preferred = [f for f in floors if f[7]]
    largest = max(start_preferred or preferred or floors, key=lambda f: f[4])

    sx = largest[5]
    sy = largest[6]
    margin = 0.8
    gxmin, gxmax = xmin + margin, xmax - margin
    gymin, gymax = ymin + margin, ymax - margin
    if gxmin < gxmax:
        sx = max(gxmin, min(gxmax, sx))
    if gymin < gymax:
        sy = max(gymin, min(gymax, sy))

    return {
        "has_bounds": 1,
        "spawn_x": sx,
        "spawn_y": sy,
        "spawn_yaw": 0.0,
        "bounds": f"{xmin:.3f} {xmax:.3f} {ymin:.3f} {ymax:.3f}",
    }


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: world_profile.py WORLD")

    profile = extract_profile(ET.parse(sys.argv[1]).getroot())
    print(f"FINAL_HAS_BOUNDS={profile['has_bounds']}")
    print(f"FINAL_SPAWN_X={profile['spawn_x']:.3f}")
    print(f"FINAL_SPAWN_Y={profile['spawn_y']:.3f}")
    print(f"FINAL_SPAWN_YAW={profile['spawn_yaw']:.0f}")
    print(f"FINAL_BOUNDS='{profile['bounds']}'")


if __name__ == "__main__":
    main()
