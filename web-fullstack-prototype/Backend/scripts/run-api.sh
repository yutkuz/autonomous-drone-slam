#!/usr/bin/env bash
set -euo pipefail

export DOTNET_ROOT="${DOTNET_ROOT:-/home/emirhanubuntu/.dotnet}"
export PATH="$DOTNET_ROOT:/home/emirhanubuntu/.dotnet/tools:$PATH"

cd "$(dirname "$0")/.."
dotnet run --project DroneSlam.Api --urls http://localhost:5090
