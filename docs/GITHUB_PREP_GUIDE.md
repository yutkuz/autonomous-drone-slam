# Repository Maintenance Guide

This document records the repository rules used for publishing and maintaining the project.

## Repository Layout

```text
autonomous-drone-slam/
  README.md
  .gitignore
  requirements-demo.txt
  requirements-test.txt
  THIRD_PARTY_NOTICES.md
  .github/workflows/ci.yml
  docs/
    REPO_STRUCTURE.md
    GITHUB_PREP_GUIDE.md
    presentation/
    assets/
  reports/
    experiment_summary.md
  tests/
    test_world_profile.py
  final-benchmark-experiment/
    README.md
    scripts/
    slam_ws/src/
    worlds/
  experiment-archive/
    01-baseline/
    02-rtabmap-improvement/
    ...
    11-turning-tunnel/
  web-interface/
  web-fullstack-prototype/
```

## Files Excluded From Git

Large outputs, local build files and machine-specific caches are kept outside the repository:

- `final-benchmark-experiment/outputs/`
- `final-benchmark-experiment/yenicikti/`
- `final-benchmark-experiment/logs/`
- `final-benchmark-experiment/slam_ws/build/`
- `final-benchmark-experiment/slam_ws/install/`
- `final-benchmark-experiment/slam_ws/log/`
- `experiment-archive/*/outputs/`
- `experiment-archive/*/yenicikti/`
- `experiment-archive/*/logs/`
- `experiment-archive/*/slam_ws/build/`
- `experiment-archive/*/slam_ws/install/`
- `experiment-archive/*/slam_ws/log/`
- `web-interface/node_modules/`
- `web-fullstack-prototype/**/obj/`
- `web-fullstack-prototype/**/bin/`
- `*.db`, `*.ply`, `*.glb`, `*.obj`, `*.bag`
- raw RGB/depth folders, datasets, model weights and local zip archives

## Dependency Files

- `requirements-demo.txt`: helper scripts and local render/demo dependencies.
- `requirements-test.txt`: dependencies required by the lightweight test suite.

The project depends mainly on ROS 2, Gazebo and RTAB-Map system packages, so Python requirements only cover the Python-side tooling.

## License Notes

`THIRD_PARTY_NOTICES.md` lists the main third-party technologies used by the project, including ROS 2, Gazebo, RTAB-Map, sjtu_drone, Three.js, obj2gltf, ASP.NET Core, EF Core, NumPy, OpenCV and Pillow.

## Validation

Run the lightweight checks before publishing changes:

```bash
pytest -q
node --check web-interface/app.js
node --check web-fullstack-prototype/Frontend/app.js
```

Check that ignored artifact types are still excluded:

```bash
git check-ignore -v final-benchmark-experiment/yenicikti/20260621_202718_maps12_general_benchmark_9dk/rtabmap_export/rtabmap.db
git check-ignore -v web-interface/node_modules/three/build/three.module.js
```

Before pushing, verify that large generated artifacts are not staged.
