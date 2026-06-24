#!/usr/bin/env bash
set -euo pipefail

SA_PASSWORD="${SA_PASSWORD:-DroneSlam!2026Db}"
MSSQL_PID="${MSSQL_PID:-Developer}"

echo "MSSQL Server 2022 local kurulum basliyor."
echo "Database: DroneSlamDb"
echo "SA kullanicisi: sa"
echo "SA sifresi: ${SA_PASSWORD}"
echo

if ! command -v sudo >/dev/null 2>&1; then
  echo "sudo bulunamadi. MSSQL kurulumu icin sudo gerekli."
  exit 1
fi

curl -fsSL https://packages.microsoft.com/keys/microsoft.asc \
  | sudo gpg --dearmor --yes -o /usr/share/keyrings/microsoft-prod.gpg

echo "deb [arch=amd64,arm64,armhf signed-by=/usr/share/keyrings/microsoft-prod.gpg] https://packages.microsoft.com/ubuntu/22.04/mssql-server-2022 jammy main" \
  | sudo tee /etc/apt/sources.list.d/mssql-server-2022.list >/dev/null

echo "deb [arch=amd64,arm64,armhf signed-by=/usr/share/keyrings/microsoft-prod.gpg] https://packages.microsoft.com/ubuntu/22.04/prod jammy main" \
  | sudo tee /etc/apt/sources.list.d/microsoft-prod.list >/dev/null

sudo apt-get update
sudo apt-get install -y curl gnupg apt-transport-https software-properties-common
sudo ACCEPT_EULA=Y apt-get install -y mssql-server mssql-tools18 unixodbc-dev

sudo ACCEPT_EULA=Y MSSQL_PID="${MSSQL_PID}" MSSQL_SA_PASSWORD="${SA_PASSWORD}" /opt/mssql/bin/mssql-conf -n setup
sudo systemctl enable mssql-server
sudo systemctl start mssql-server

echo 'export PATH="$PATH:/opt/mssql-tools18/bin"' >> "$HOME/.bashrc"
export PATH="$PATH:/opt/mssql-tools18/bin"

echo "SQL Server servis durumu:"
systemctl is-active mssql-server

echo "SQL Server baglanti testi:"
/opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P "${SA_PASSWORD}" -C -Q "SELECT @@VERSION"

echo
echo "MSSQL kurulumu tamamlandi."
echo "Connection string:"
echo "Server=localhost,1433;Database=DroneSlamDb;User Id=sa;Password=${SA_PASSWORD};TrustServerCertificate=True;Encrypt=False"
