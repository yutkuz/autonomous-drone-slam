#!/usr/bin/env bash
# Final benchmark live test: Gazebo + RTAB-Map + general autonomous explorer. No snapshot/export.
set -euo pipefail

FINAL_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WORLD="${1:-${FINAL_ROOT}/worlds/general_slam_benchmark.world}"
SESSION="${FINAL_SESSION:-final_benchmark_live}"
LOG_DIR="${FINAL_ROOT}/logs/live_$(date +%Y%m%d_%H%M%S)"

mkdir -p "${LOG_DIR}"
tmux kill-session -t "${SESSION}" 2>/dev/null || true

eval "$("${FINAL_ROOT}/scripts/world_profile.py" "${WORLD}")"

ENV_EXPORTS="export FINAL_SPAWN_X='${FINAL_SPAWN_X:-0}'; export FINAL_SPAWN_Y='${FINAL_SPAWN_Y:-0}'; export FINAL_SPAWN_YAW='${FINAL_SPAWN_YAW:-0}'; export FINAL_BOUNDS='${FINAL_BOUNDS:-}'; export FINAL_HAS_BOUNDS='${FINAL_HAS_BOUNDS:-0}'"

tmux new-session -d -s "${SESSION}" -n gazebo bash
tmux send-keys -t "${SESSION}:gazebo" "${ENV_EXPORTS}; source '${FINAL_ROOT}/scripts/env.sh'; ros2 launch sjtu_drone_bringup sjtu_drone_bringup.launch.py world:='${WORLD}' 2>&1 | tee '${LOG_DIR}/bringup.log'" C-m

sleep 10

tmux new-window -t "${SESSION}" -n rtabmap bash
tmux send-keys -t "${SESSION}:rtabmap" "${ENV_EXPORTS}; source '${FINAL_ROOT}/scripts/env.sh'; ros2 launch sjtu_drone_bringup rtabmap_lidar_depth.launch.py rtabmapviz:=true 2>&1 | tee '${LOG_DIR}/rtabmap.log'" C-m

sleep 8

tmux new-window -t "${SESSION}" -n explorer bash
tmux send-keys -t "${SESSION}:explorer" "${ENV_EXPORTS}; source '${FINAL_ROOT}/scripts/env.sh'; python3 '${FINAL_ROOT}/scripts/autonomous_explorer.py' --altitude 1.45 --duration 540 2>&1 | tee '${LOG_DIR}/explorer.log'" C-m

echo "Final benchmark live started."
echo "World: ${WORLD}"
echo "Spawn: ${FINAL_SPAWN_X:-0}, ${FINAL_SPAWN_Y:-0}"
echo "Bounds: ${FINAL_BOUNDS:-none}"
echo "Logs: ${LOG_DIR}"
echo "Watch: tmux attach -t ${SESSION}"
