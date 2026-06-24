# SLAM Sunum Taslağı - 15 Sayfa

Bu dosya, proje sunumu 15 sayfaya çıkarılmak istenirse kullanılabilecek sade slayt akışıdır.

## 1. Başlık

**Kâşif Drone SLAM Sistemi**

ROS 2, Gazebo ve RTAB-Map ile kapalı alanlarda otonom drone tabanlı 3B haritalama.

## 2. Problem Tanımı

Kapalı alanlarda GPS sinyali yetersizdir. Tarihi yapılar, müzeler, mağaralar ve dar koridorlu alanlarda manuel haritalama zaman alır, maliyetlidir ve risklidir.

## 3. Projenin Amacı

Drone'un simülasyon ortamında otonom veya kontrollü şekilde hareket ederek RTAB-Map ile 3B nokta bulutu, veritabanı ve görsel çıktı üretmesi hedeflenmiştir.

## 4. Kullanılan Teknolojiler

- Ubuntu 22.04
- ROS 2 Humble
- Gazebo
- sjtu_drone
- RTAB-Map
- RGB-D/depth kamera
- LiDAR/point cloud
- Web tabanlı görselleştirme

## 5. Sistem Mimarisi

Gazebo drone ve sensör verilerini üretir. ROS 2 topic yapısı bu verileri taşır. RTAB-Map haritalama yapar. Otonom explorer drone hareket kararlarını üretir. WebDemo sonuçları görselleştirir.

## 6. SLAM Yaklaşımı

RTAB-Map, kamera/depth, LiDAR ve odometri verilerini kullanarak 3B harita üretir. Çıktılar `rtabmap.db`, `rtabmap_cloud.ply`, pose dosyaları, render görselleri ve mesh dosyalarıdır.

## 7. Maps1-Maps2: Başlangıç ve SLAM Hattı

Maps1 ilk çalışan baseline olarak korundu. Maps2'de kamera açısı, LiDAR hizası ve RTAB-Map parametreleri iyileştirildi. Amaç daha düzenli nokta bulutu alabilmekti.

## 8. Maps3-Maps4: Tünel ve Loop Closure

Maps3 ile tünel/koridor yapısı denendi. Maps4'te daha geniş galeri ortamı ve gidiş-dönüş rota ile loop closure ihtimali artırıldı.

## 9. Maps5-Maps6: Nokta Bulutu ve Sensör Kapsaması

Maps5'te yavaş rota ve feature açısından zengin ortamla daha temiz nokta bulutu hedeflendi. Maps6'da sağ ve sol depth kameralar eklenerek yan yüzeylerin daha iyi algılanması amaçlandı.

## 10. Maps7-Maps8: Otonom Coverage

Maps7 ile visited-grid ve recovery mantığına geçildi. Maps8'de waypoint'siz yön seçimi, LiDAR/depth açıklık skoru, wall-band coverage ve stuck recovery denendi.

## 11. Maps9: Kontrollü Waypoint Denemesi

Maps9'da temiz ve tekrarlanabilir tünel SLAM çıktısı almak için kontrollü waypoint rotası kullanıldı. Bu deneyin amacı otonomluk değil, temiz sonuç üretmekti.

## 12. Maps10-Maps12: Genel Otonom Algoritma

Maps10, Maps11 ve Maps12'de aynı genel otonom explorer kullanıldı. Haritaya özel waypoint yazılmadı. Drone kararlarını visited-grid, açıklık skoru, geofence ve recovery davranışlarıyla verdi.

## 13. Final Sonuçlar

| Ortam türü | Pose | Link | Ham nokta | Voxel sonrası |
| --- | ---: | ---: | ---: | ---: |
| Genel oda/koridor | 166 | 391 | 1.281.401 | 1.032.035 |
| Dönüşlü tünel | 152 | 443 | 1.133.121 | 599.763 |
| Loop benchmark | 151 | 373 | 1.498.090 | 845.870 |

## 14. Web Arayüzü

WebDemo, harita senaryolarını, final çıktı önizlemelerini, 3B nokta bulutlarını, kamera/depth görüntülerini ve LiDAR/fusion önizlemelerini tek panelde gösterir.

## 15. Sonuç ve Gelecek Çalışma

Sistem farklı harita türlerinde RTAB-Map tabanlı 3B çıktı üretebilmiştir. Tam kapsama garanti edilmez; çünkü algoritma global frontier planner değildir. Gelecekte frontier planner, daha güçlü path planning, gerçek drone entegrasyonu ve daha uzun süreli saha testleri eklenebilir.
