# WebDemo2

Drone SLAM final sunumu icin .NET 8 backend, MSSQL metadata veritabani ve web frontend.

## Mimari

- `Backend/DroneSlam.Domain`: Entity katmani
- `Backend/DroneSlam.Application`: DTO, service ve repository arayuzleri
- `Backend/DroneSlam.Infrastructure`: EF Core MSSQL DbContext, repository ve Project-Final import servisi
- `Backend/DroneSlam.Api`: Controller, dosya servis endpointleri ve frontend hosting
- `Frontend`: Web arayuzu

## Veri Modeli

Buyuk SLAM dosyalari MSSQL icine gomulmez. `rtabmap.db`, `.ply`, `.png`, `.obj` gibi dosyalar diskte kalir.
MSSQL map adi, tarih, dosya yolu, dosya boyutu, pose/link/nokta sayisi ve sunum notlarini tutar.

## Local MSSQL

Varsayilan connection string:

```text
Server=localhost,1433;Database=DroneSlamDb;User Id=sa;Password=DroneSlam!2026Db;TrustServerCertificate=True;Encrypt=False
```

Kurulum:

```bash
cd /home/emirhanubuntu/Desktop/Project-Final/WebDemo2/Backend
./scripts/install-mssql-local.sh
```

## Calistirma

```bash
cd /home/emirhanubuntu/Desktop/Project-Final/WebDemo2/Backend
./scripts/migrate-db.sh
./scripts/run-api.sh
./scripts/import-maps.sh
```

Web:

```text
http://localhost:5090
```

## API

- `GET /api/maps`
- `GET /api/maps/{id}`
- `POST /api/maps/import`
- `GET /api/maps/{id}/assets/{assetType}/file`
