#!/usr/bin/env bash
set -euo pipefail

export DOTNET_ROOT="${DOTNET_ROOT:-/home/emirhanubuntu/.dotnet}"
export PATH="$DOTNET_ROOT:/home/emirhanubuntu/.dotnet/tools:$PATH"

cd "$(dirname "$0")/.."
dotnet ef database update --project DroneSlam.Infrastructure --startup-project DroneSlam.Api
