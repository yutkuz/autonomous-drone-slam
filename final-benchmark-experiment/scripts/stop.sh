#!/usr/bin/env bash
# Sadece final benchmark ve ilgili test proseslerini durdurur. Ana slam_ws dokunulmaz.
echo "Final benchmark prosesleri durduruluyor..."
tmux kill-session -t final_benchmark_live 2>/dev/null || true
tmux kill-session -t final_benchmark_run 2>/dev/null || true
pkill -f "sjtu_drone_bringup" 2>/dev/null || true
pkill -f "rtabmap_lidar_depth" 2>/dev/null || true
pkill -f "autonomous_explorer.py" 2>/dev/null || true
pkill -f "room_explorer_professional" 2>/dev/null || true
pkill -f "waypoint_explorer.py" 2>/dev/null || true
pkill -f "save_live_bundle.py" 2>/dev/null || true
pkill -f "rtabmap-export" 2>/dev/null || true
pkill -f "rtabmap_viz" 2>/dev/null || true
pkill -f "rtabmap_slam" 2>/dev/null || true
pkill -f "rgbd_sync" 2>/dev/null || true
pkill -f "odom_frame_fixer" 2>/dev/null || true
pkill -f "camera_frame_fixer" 2>/dev/null || true
# Gazebo
pkill -f "gzserver" 2>/dev/null || true
pkill -f "gzclient" 2>/dev/null || true
pkill -f "rviz2" 2>/dev/null || true
echo "Final benchmark durduruldu."
