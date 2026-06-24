# Final Benchmark Experiment

Bu klasör, projenin son SLAM deneyi için kullanılan senaryo paketidir. İçinde Gazebo dünyası, ROS 2 workspace dosyaları, çalıştırma scriptleri ve RTAB-Map tabanlı otonom keşif akışı bulunur.

## Amaç

Bu deneyde, önceki sürümlerde geliştirilen genel otonom keşif algoritması daha zor bir benchmark senaryosunda denenir. Algoritmaya bu ortama özel sabit rota, waypoint listesi veya haritaya göre yazılmış kural eklenmez.

## Senaryo

- Sağ-sol dönüşlü dar tünel koridorları.
- Uzun koridorlar, 90 derece dönüşler ve geri bağlanan bölümler.
- SLAM tarafından algılanabilecek kutu, silindir, sütun ve ağaç benzeri engeller.
- Gazebo collision/visual geometrisi olarak tanımlanmış duvar, zemin ve engeller.

## Canlı Çalıştırma

```bash
cd /home/emirhanubuntu/Desktop/Project-Final/final-benchmark-experiment
./scripts/start_live.sh
```

`start_live.sh` kayıt/export almaz. Sadece Gazebo, RTAB-Map ve genel otonom explorer başlatılarak canlı gözlem yapılır.

## Durdurma

```bash
cd /home/emirhanubuntu/Desktop/Project-Final/final-benchmark-experiment
./scripts/stop.sh
```

## Otonom Mantık

- Dinamik grid üzerinde ziyaret edilen alanları takip eder.
- LiDAR/depth nokta bulutundan lokal açıklık değeri hesaplar.
- Daha az gezilen ve açık yönlere ağırlık verir.
- Geofence bilgisini world dosyasındaki zemin parçalarından otomatik çıkarır.
- İlerleme olmazsa aynı yönü sürekli denemez; başarısız yönü geçici hafızaya alır, geri/yan kaçış ve yeni yön seçimi yapar.

## SLAM

RTAB-Map kullanılır. Drone tünel duvarlarını, sütunları, kutuları ve ağaç benzeri engelleri nokta bulutu olarak algılayıp haritaya dahil eder.
