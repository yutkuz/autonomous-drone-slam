# Repository Structure

This document describes the public repository layout for the Autonomous Drone SLAM project.

```text
autonomous-drone-slam/
  README.md
  .gitignore
  requirements-demo.txt
  requirements-test.txt
  pytest.ini
  THIRD_PARTY_NOTICES.md
  .github/
    workflows/
      ci.yml
  docs/
    GITHUB_PREP_GUIDE.md
    REPO_STRUCTURE.md
    presentation/
      slam_sunum_15_sayfa.md
    assets/
      README.md
      gazebo/
      outputs/
      web-ui/
  reports/
    experiment_summary.md
  tests/
    test_world_profile.py
  final-benchmark-experiment/
  experiment-archive/
    01-baseline/
    02-rtabmap-improvement/
    ...
    11-turning-tunnel/
  web-interface/
  web-fullstack-prototype/
```

## Experiment Folders

`final-benchmark-experiment/` contains the active benchmark scenario. Earlier iterations are kept under `experiment-archive/` with numbered, descriptive folder names.

Each experiment folder can contain:

- `README.md`
- `scripts/`
- `slam_ws/src/`
- `worlds/`

Generated experiment files are excluded from Git:

- `outputs/`
- `yenicikti/`
- `logs/`
- `slam_ws/build/`
- `slam_ws/install/`
- `slam_ws/log/`

## Web Folders

- `web-interface/`: static web interface for reviewing experiment results.
- `web-fullstack-prototype/`: optional .NET backend and frontend prototype.

## Documentation Assets

Small PNG/JPEG previews are stored under `docs/assets/` for README, reports and presentation material. Full RTAB-Map databases, point clouds, meshes and raw RGB/depth frame folders are kept outside Git.
