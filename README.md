# Autonomous Drone SLAM

ROS 2, Gazebo ve RTAB-Map kullanılarak kapalı alanlarda drone tabanlı 3B haritalama ve otonom keşif deneyleri yürütülen proje deposudur. Proje, temel SLAM hattından başlayarak sensör füzyonu, rota kalitesi, recovery davranışları ve genel otonom keşif algoritmasına kadar ilerleyen deney serisini içerir.

Depo kod, yapılandırma, hafif testler ve dokümantasyon odaklıdır. RTAB-Map veritabanları, nokta bulutları, mesh dosyaları, build klasörleri ve ham deney çıktıları repoya dahil edilmez.

## İçerik

- `final-benchmark-experiment/`: final benchmark senaryosu, çalıştırma scriptleri ve ROS 2 workspace kaynakları.
- `experiment-archive/`: önceki deney sürümleri. Her klasör, deneyin kendi scriptlerini ve ilgili workspace dosyalarını içerir.
- `web-interface/`: statik web arayüzü. Deney sonuçlarını, görselleri ve 3B çıktı bağlantılarını sunmak için kullanılır.
- `web-fullstack-prototype/`: .NET backend ve frontend prototipi.
- `docs/`: depo yapısı, sunum taslağı ve dokümantasyon görselleri.
- `reports/`: deney sonuçlarının özetleri.
- `tests/`: ROS/Gazebo başlatmadan çalışan hafif testler.

## Çalışma Ortamı

Simülasyon ve SLAM akışı için kullanılan ana ortam:

- Ubuntu 22.04 LTS
- ROS 2 Humble
- Gazebo Classic / Gazebo 11
- RTAB-Map ve ROS 2 RTAB-Map paketleri
- Python 3.10
- colcon
- tmux
- NumPy, OpenCV ve Pillow

Web arayüzü için Python HTTP server yeterlidir. Full-stack prototip için .NET 8 SDK ve SQL Server uyumlu bir veritabanı gerekir.

## Kurulum

Depoyu klonlayın:

```bash
git clone <repo-url>
cd autonomous-drone-slam
```

Python bağımlılıklarını kurun:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-demo.txt
```

ROS 2, Gazebo ve RTAB-Map kurulumunu doğrulayın:

```bash
ros2 --help
gazebo --version
rtabmap --version
colcon --help
```

Final deney workspace'ini build edin:

```bash
cd final-benchmark-experiment
./scripts/build.sh
```

## Çalıştırma

Final benchmark deneyini başlatmak için:

```bash
cd final-benchmark-experiment
./scripts/start.sh
```

Kayıt/export almadan canlı gözlem için:

```bash
cd final-benchmark-experiment
./scripts/start_live.sh
```

Durdurma:

```bash
./scripts/stop.sh
```

Manuel çıktı kaydı:

```bash
./scripts/save.sh
```

`start.sh`, deney sonunda snapshot ve RTAB-Map export akışını otomatik çalıştırır. Sadece görsel kontrol yapılacaksa `start_live.sh` kullanılmalıdır.

## Web Arayüzü

Statik arayüz depo kökünden servis edilmelidir:

```bash
python3 -m http.server 8088 --bind 0.0.0.0 --directory .
```

Tarayıcıdan açın:

```text
http://localhost:8088/web-interface/
```

Arayüz; deney kartlarını, final çıktı önizlemelerini, nokta bulutu/mesh bağlantılarını ve kamera/depth görsellerini gösterir. Büyük `.ply`, `.db` ve `.glb` dosyaları repoda tutulmaz.

## Deney Serisi

| Deney | Amaç | Uçuş mantığı |
| --- | --- | --- |
| Maps1 | İlk çalışan baseline | Temel SLAM hattı |
| Maps2 | RTAB-Map hattını iyileştirme | Kontrollü oda denemesi |
| Maps3 | Tünel/koridor denemesi | Kontrollü rota |
| Maps4 | Geniş galeri ve loop closure | Gidiş-dönüş rota |
| Maps5 | Daha temiz nokta bulutu | Yavaş kontrollü rota |
| Maps6 | Sağ/sol depth kamera | Kontrollü rota ve ek sensör |
| Maps7 | Otonom coverage başlangıcı | visited-grid ve recovery |
| Maps8 | Waypoint'siz otonom deneme | coverage skorlaması |
| Maps9 | Temiz tünel çıktısı | kontrollü waypoint |
| Maps10 | Genel otonom explorer | haritaya özel waypoint yok |
| Maps11 | Zorlu dönüşlü tünel | genel otonom algoritma |
| Maps12 | Benchmark benzeri ortam | genel otonom algoritma |

## Final Sonuçlar

| Ortam türü | Pose | Link | Ham nokta | Voxel sonrası nokta | RTAB-Map DB |
| --- | ---: | ---: | ---: | ---: | ---: |
| Genel oda/koridor | 166 | 391 | 1.281.401 | 1.032.035 | 577 MB |
| Dönüşlü tünel | 152 | 443 | 1.133.121 | 599.763 | 450 MB |
| Loop oda/koridor benchmark | 151 | 373 | 1.498.090 | 845.870 | 584 MB |

Sonuçlar, aynı genel otonom keşif algoritmasının farklı geometrilerde RTAB-Map çıktısı üretebildiğini gösterir. Sistem global frontier planner değildir; bu nedenle tam kapsama garanti edilmez.

## Çıktı Dosyaları

- `rtabmap.db`: RTAB-Map veritabanı.
- `rtabmap_cloud.ply`: final 3B nokta bulutu.
- `rtabmap_cloud_poses.txt`: poz/trajectory kaydı.
- `rtabmap_cloud_camera_poses.txt`: kamera pozları.
- `render_bev.png`: üstten 2B harita görünümü.
- `mesh.obj`, `mesh_unlit.glb`: mesh ve web gösterimi için çıktı.
- `live_snapshot/camera`: RGB ve depth kamera görüntüleri.
- `live_snapshot/lidar`: LiDAR nokta bulutu önizlemesi.
- `live_snapshot/fused_slam`: canlı birleşik SLAM snapshot.

## Repoya Dahil Edilmeyen Dosyalar

Aşağıdaki dosyalar büyük, makineye özel veya yeniden üretilebilir olduğu için Git dışında tutulur:

- `final-benchmark-experiment/outputs/`
- `final-benchmark-experiment/yenicikti/`
- `final-benchmark-experiment/logs/`
- `final-benchmark-experiment/slam_ws/build/`
- `final-benchmark-experiment/slam_ws/install/`
- `final-benchmark-experiment/slam_ws/log/`
- `experiment-archive/*/outputs/`
- `experiment-archive/*/yenicikti/`
- `experiment-archive/*/logs/`
- `experiment-archive/*/slam_ws/build/`
- `experiment-archive/*/slam_ws/install/`
- `experiment-archive/*/slam_ws/log/`
- `*.db`, `*.ply`, `*.glb`, `*.obj`, `*.bag`
- `rgb/`, `depth/`, `datasets/`, `models/`, `weights/`
- `node_modules/`

## Testler

```bash
pip install -r requirements-test.txt
pytest -q
```

Frontend syntax kontrolü:

```bash
node --check web-interface/app.js
node --check web-fullstack-prototype/Frontend/app.js
```

## CI

`.github/workflows/ci.yml` şu kontrolleri çalıştırır:

- Python testleri
- statik web arayüzü JavaScript syntax check
- full-stack prototip frontend JavaScript syntax check

CI, Gazebo/RTAB-Map/ROS 2 simülasyonu başlatmaz ve büyük deney çıktısı yüklemez.

## Lisans ve Üçüncü Parti Bileşenler

Üçüncü parti bileşenler ve lisans notları için `THIRD_PARTY_NOTICES.md` dosyasına bakın.

## Ek Dokümanlar

- `docs/REPO_STRUCTURE.md`: depo klasör yapısı.
- `docs/GITHUB_PREP_GUIDE.md`: yayınlama ve bakım kontrol listesi.
- `docs/presentation/slam_sunum_15_sayfa.md`: sunum taslağı.
- `reports/experiment_summary.md`: deney sonuçları özeti.
