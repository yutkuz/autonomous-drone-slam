#!/usr/bin/env bash
# Final benchmark SLAM ciktisini kaydeder.
set -euo pipefail

FINAL_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
source "${FINAL_ROOT}/scripts/env.sh"

LABEL="${LABEL:-final_benchmark_$(date +%Y-%m-%d_%H-%M-%S)}"
OUT_DIR="${FINAL_ROOT}/outputs/${LABEL}"
mkdir -p "${OUT_DIR}"

echo "=== Final benchmark cikti kaydediliyor ==="
echo "Hedef: ${OUT_DIR}"

python3 "${FINAL_ROOT}/scripts/save_slam_snapshot.py" \
  --output-dir "${OUT_DIR}" \
  --label "${LABEL}"

echo "Kaydedildi: ${OUT_DIR}"
