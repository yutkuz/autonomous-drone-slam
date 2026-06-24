#!/usr/bin/env bash
set -euo pipefail

export DOTNET_ROOT="${DOTNET_ROOT:-/home/emirhanubuntu/.dotnet}"
export PATH="$DOTNET_ROOT:/home/emirhanubuntu/.dotnet/tools:/opt/mssql-tools18/bin:$PATH"

cd "$(dirname "$0")/.."

echo "EF migration uygulanıyor..."
dotnet ef database update --project DroneSlam.Infrastructure --startup-project DroneSlam.Api

echo "API baslatiliyor..."
if pgrep -f "DroneSlam.Api.*localhost:5090" >/dev/null; then
  echo "API zaten calisiyor."
else
  nohup dotnet run --project DroneSlam.Api --urls http://localhost:5090 > /tmp/webdemo2-api.log 2>&1 &
  sleep 8
fi

echo "Project-Final/Maps* DB import baslatiliyor..."
curl -fsS -X POST http://localhost:5090/api/maps/import
echo
echo "Tamamlandi. Web: http://localhost:5090"
