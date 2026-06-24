# Drone SLAM WebDemo

Bu klasor, Project-Final altindaki Maps2-Maps8 ciktilarini sunum icin tek web panelinde gosterir.

## Calistirma

Project-Final kok klasorunden servis etmek gerekir; boylece WebDemo, `../experiment-archive/...` ve `../final-benchmark-experiment` ciktilarina erisebilir.

```bash
cd /home/emirhanubuntu/Desktop/Project-Final
python3 -m http.server 8088
```

Tarayici:

```text
http://localhost:8088/WebDemo/
```

## Icerik

- BEV ve side PNG SLAM gorselleri
- Kamera, lidar ve fused SLAM snapshotlari
- RTAB-Map DB dosya baglantilari
- PLY nokta bulutu baglantilari
- Tarayici icinde 3B PLY goruntuleyici

Not: Mevcut klasorlerde video dosyasi bulunmadigi icin video alani eklenmedi. Video kayitlari
eklenirse `app.js` icindeki map manifestine `video` yolu eklenerek sayfaya dahil edilebilir.
