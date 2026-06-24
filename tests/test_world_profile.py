import importlib.util
import pathlib
import xml.etree.ElementTree as ET


ROOT = pathlib.Path(__file__).resolve().parents[1]
WORLD_PROFILE = ROOT / "final-benchmark-experiment" / "scripts" / "world_profile.py"


def load_world_profile():
    spec = importlib.util.spec_from_file_location("world_profile", WORLD_PROFILE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_values_fills_missing_numbers_with_default():
    module = load_world_profile()

    assert module.values("1.5 bad", 4, default=-1.0) == [1.5, -1.0, -1.0, -1.0]


def test_combined_pose_applies_parent_yaw():
    module = load_world_profile()

    x, y, z, yaw = module.combined_pose(
        "0 0 0 0 0 1.57079632679",
        "1 0 2 0 0 0",
    )

    assert round(x, 3) == 0.0
    assert round(y, 3) == 1.0
    assert round(z, 3) == 2.0
    assert round(yaw, 3) == 1.571


def test_extract_profile_returns_spawn_and_bounds_for_floor():
    module = load_world_profile()
    root = ET.fromstring(
        """
        <sdf version="1.6">
          <world name="test">
            <model name="room">
              <static>true</static>
              <pose>10 0 0 0 0 0</pose>
              <link name="start_floor">
                <pose>0 0 0 0 0 0</pose>
                <collision name="floor_collision">
                  <geometry><box><size>8 4 0.1</size></box></geometry>
                </collision>
              </link>
            </model>
          </world>
        </sdf>
        """
    )

    profile = module.extract_profile(root)

    assert profile["has_bounds"] == 1
    assert round(profile["spawn_x"], 3) == 10.0
    assert round(profile["spawn_y"], 3) == 0.0
    assert profile["bounds"] == "6.000 14.000 -2.000 2.000"
