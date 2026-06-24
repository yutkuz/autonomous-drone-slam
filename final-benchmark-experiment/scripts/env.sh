#!/usr/bin/env bash
# Final benchmark ortam kurulumu
# Final benchmark workspace install dizinini kullanir
set -euo pipefail

FINAL_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FINAL_WS="${FINAL_ROOT}/slam_ws"

# Sistem ROS2
if [ -f /opt/ros/humble/setup.bash ]; then
  set +u; source /opt/ros/humble/setup.bash; set -u
else
  echo "HATA: ROS 2 Humble bulunamadi." >&2; return 1 2>/dev/null || exit 1
fi

# Gazebo Classic yerel kurulum (Maps1 ile ayni, sadece env degiskenleri)
GAZEBO_LOCAL="${HOME}/Desktop/bugra/gazebo_classic_local"
if [ -d "${GAZEBO_LOCAL}" ]; then
  export PATH="${GAZEBO_LOCAL}/usr/bin:${GAZEBO_LOCAL}/opt/ros/humble/bin:${PATH}"
  export LD_LIBRARY_PATH="${GAZEBO_LOCAL}/usr/lib/x86_64-linux-gnu:${GAZEBO_LOCAL}/usr/lib:${GAZEBO_LOCAL}/usr/lib/x86_64-linux-gnu/gazebo-11/plugins:${GAZEBO_LOCAL}/opt/ros/humble/lib:${GAZEBO_LOCAL}/opt/ros/humble/lib/x86_64-linux-gnu:${LD_LIBRARY_PATH:-}"
  export CMAKE_PREFIX_PATH="${GAZEBO_LOCAL}/opt/ros/humble:${GAZEBO_LOCAL}/usr:${CMAKE_PREFIX_PATH:-}"
  export AMENT_PREFIX_PATH="${GAZEBO_LOCAL}/opt/ros/humble:${AMENT_PREFIX_PATH:-}"
  export PYTHONPATH="${GAZEBO_LOCAL}/opt/ros/humble/lib/python3.10/site-packages:${GAZEBO_LOCAL}/opt/ros/humble/local/lib/python3.10/dist-packages:${PYTHONPATH:-}"
  export GAZEBO_PLUGIN_PATH="${GAZEBO_LOCAL}/usr/lib/x86_64-linux-gnu/gazebo-11/plugins:${GAZEBO_LOCAL}/opt/ros/humble/lib:${GAZEBO_PLUGIN_PATH:-}"
  export GAZEBO_MODEL_PATH="${GAZEBO_LOCAL}/usr/share/gazebo-11/models:${GAZEBO_MODEL_PATH:-}"
  export GAZEBO_RESOURCE_PATH="${GAZEBO_LOCAL}/usr/share/gazebo-11:${GAZEBO_LOCAL}/usr/share/gazebo:${GAZEBO_RESOURCE_PATH:-}"
fi

# RTAB-Map yerel
RTABMAP_LOCAL="${HOME}/Desktop/calismalar/versiyon11_px4_offboard_rgbd_slam/local/opt/ros/humble"
if [ -d "${RTABMAP_LOCAL}" ]; then
  export LD_LIBRARY_PATH="${RTABMAP_LOCAL}/lib:${RTABMAP_LOCAL}/lib/x86_64-linux-gnu:${LD_LIBRARY_PATH:-}"
  export AMENT_PREFIX_PATH="${RTABMAP_LOCAL}:${AMENT_PREFIX_PATH:-}"
  export PYTHONPATH="${RTABMAP_LOCAL}/local/lib/python3.10/dist-packages:${PYTHONPATH:-}"
fi

# Final benchmark kendi workspace dizinini kullanir
if [ -f "${FINAL_WS}/install/setup.bash" ]; then
  set +u; source "${FINAL_WS}/install/setup.bash"; set -u
else
  echo "UYARI: Final benchmark workspace henuz build edilmemis. Once ./scripts/build.sh calistir." >&2
fi

export FINAL_ROOT FINAL_WS
