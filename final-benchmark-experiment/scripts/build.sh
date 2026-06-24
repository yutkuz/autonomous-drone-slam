#!/usr/bin/env bash
set -euo pipefail

FINAL_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
source "${FINAL_ROOT}/scripts/env.sh"

echo "=== Final benchmark workspace build ==="
echo "Workspace: ${FINAL_WS}"
echo "Maps1 (~/slam_ws) etkilenmez."
echo

cd "${FINAL_WS}"
colcon build --symlink-install \
  --packages-select sjtu_drone_description sjtu_drone_bringup sjtu_drone_control drone_autonomy \
  --cmake-args -DCMAKE_BUILD_TYPE=Release

echo
echo "Build tamamlandi. Final benchmark hazir."
