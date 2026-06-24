# Deney Sonuçları Özeti

Bu rapor, final SLAM deneylerinde elde edilen temel çıktıları ve repoda tutulmayan büyük artifact türlerini özetler.

## Çıktı Politikası

RTAB-Map veritabanları, PLY nokta bulutları, mesh dosyaları, canlı snapshotlar ve render çıktıları büyük dosyalardır. Bu dosyalar Git içinde tutulmaz; deney çalıştırıldığında yeniden üretilir veya harici depolamada saklanır.

Repoda yalnızca küçük dokümantasyon görselleri bulunur:

- `docs/assets/outputs/maps10_top_preview.png`
- `docs/assets/outputs/maps11_bev.png`
- `docs/assets/outputs/maps12_bev.png`
- `docs/assets/outputs/rtabmap_database_viewer.jpeg`
- `docs/assets/web-ui/`
- `docs/assets/gazebo/`

## Final Deney Karşılaştırması

| Ortam türü | Pose | Link | Ham nokta | Voxel sonrası nokta | DB boyutu |
| --- | ---: | ---: | ---: | ---: | ---: |
| Genel oda/koridor | 166 | 391 | 1.281.401 | 1.032.035 | 577 MB |
| Dönüşlü tünel | 152 | 443 | 1.133.121 | 599.763 | 450 MB |
| Loop oda/koridor benchmark | 151 | 373 | 1.498.090 | 845.870 | 584 MB |

## Değerlendirme

Genel oda/koridor ortamında voxel sonrası nokta sayısı en yüksektir. Dönüşlü tünel ortamında dar geçişler ve keskin dönüşler nedeniyle nokta yoğunluğu daha sınırlı kalmıştır. Loop oda/koridor benchmark ortamında daha karmaşık geometriye rağmen anlamlı bir SLAM çıktısı elde edilmiştir.

## Sınırlılıklar

Kullanılan otonom algoritma global frontier planner değildir. Drone lokal sensör verisi, visited-grid hafızası ve recovery davranışlarıyla karar verir. Bu nedenle tam kapsama garanti edilmez.

## Repoya Dahil Edilmeyen Sonuç Dosyaları

Aşağıdaki dosyalar yerel deney klasörlerinde bulunabilir ancak Git'e eklenmez:

- `experiment-archive/10-general-autonomous/yenicikti/.../rtabmap_export/rtabmap.db`
- `experiment-archive/11-turning-tunnel/yenicikti/.../rtabmap_export/rtabmap_cloud.ply`
- `final-benchmark-experiment/yenicikti/.../rtabmap_export/mesh_unlit.glb`
- `final-benchmark-experiment/outputs/`
- `final-benchmark-experiment/logs/`
- `experiment-archive/*/outputs/`
- `experiment-archive/*/logs/`
