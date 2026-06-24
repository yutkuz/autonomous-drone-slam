const maps = [
  {
    id: "maps1",
    name: "Maps1",
    title: "Maps1 Başlangıç Çalışması",
    label: "Ham",
    quality: "warn",
    period: "manuel",
    run: "../experiment-archive/01-baseline/outputs/2026-05-30_16-53-14",
    summary: "İlk yüklenen çalışan proje. Sonraki sürümler için referans ve acil sunum alternatifi olarak tutuldu.",
    stats: { poses: "-", links: "-", raw: "-", voxel: "-", db: "3.0 GB" },
    assets: {
      bev: "../experiment-archive/01-baseline/outputs/2026-05-30_16-53-14/cloud_map_top_preview.png",
      side: "",
      ply: "../experiment-archive/01-baseline/outputs/2026-05-30_16-53-14/cloud_map_snapshot.ply",
      rawPly: "",
      meshObj: "",
      meshPreviewObj: "",
      meshMtl: "",
      meshGlb: "",
      meshPng: "",
      db: "../experiment-archive/01-baseline/outputs/2026-05-30_16-53-14/rtabmap.db",
      front: "",
      depth: "",
      left: "",
      right: "",
      lidar: "",
      fused: "../experiment-archive/01-baseline/outputs/2026-05-30_16-53-14/cloud_map_top_preview.png",
    },
    notes: [
      "Ham çalışan referans proje olarak saklandı.",
      "Güçlü yanı: RTAB-Map veritabanı ve nokta bulutu mevcut.",
      "Eksik yanı: sonraki sürümlerdeki kamera/depth ayrımı ve kontrollü çıktı yapısı yok.",
    ],
  },
  {
    id: "maps2",
    name: "Maps2",
    title: "Feature Room Baseline",
    label: "Erken",
    quality: "bad",
    period: "4 dk",
    run: "../experiment-archive/02-rtabmap-improvement/yenicikti/20260531_205005_maps2_4dk",
    summary: "RTAB-Map SLAM akışının düzenli çıktı alınan ilk oda denemesi.",
    stats: { poses: "-", links: "-", raw: "-", voxel: "-", db: "381 MB" },
    notes: [
      "Kamera, LiDAR ve fused snapshot ayrımı başladı.",
      "Harita kullanılabilir ama final kalitesinde değil.",
      "Sonraki sürümlerde rota ve süre iyileştirildi.",
    ],
  },
  {
    id: "maps3",
    name: "Maps3",
    title: "Tünel Denemesi",
    label: "Sınırlı",
    quality: "bad",
    period: "4 dk",
    run: "../experiment-archive/03-tunnel-corridor/yenicikti/20260531_211531_maps3_4dk",
    summary: "Tünel geometrisinde kısa süreli SLAM testi. Ortam algısı çalıştı ancak kapsam sınırlı kaldı.",
    stats: { poses: 135, links: 323, raw: 1209799, voxel: 442008, db: "414 MB" },
    notes: [
      "Tünel senaryosu için ilk sonuç alındı.",
      "Kısa süre ve rota nedeniyle eksik bölgeler kaldı.",
      "Harita, daha uzun kayıt ihtiyacını gösterdi.",
    ],
  },
  {
    id: "maps4",
    name: "Maps4",
    title: "Geniş Tünel / Galeri",
    label: "Galeri",
    quality: "warn",
    period: "8 dk",
    run: "../experiment-archive/04-gallery-loop-closure/yenicikti/20260531_213738_maps4_8dk",
    summary: "Daha geniş ve uzun kayıtlı galeri ortamı. Harita boyutu büyüdü, mesh/side çıktıları eklendi.",
    stats: { poses: 214, links: 599, raw: 1894926, voxel: 595514, db: "663 MB" },
    notes: [
      "Pose sayısı yükseldi ve ortam daha büyük gezildi.",
      "Mesh denemesi üretildi ama yüzey kalitesi istenen seviyede değildi.",
      "Yan görünüm ve BEV sunum çıktıları oluştu.",
    ],
  },
  {
    id: "maps5",
    name: "Maps5",
    title: "Yavaş Rota ve RTAB-Map Ayarı",
    label: "Güçlü",
    quality: "ok",
    period: "9 dk",
    run: "../experiment-archive/05-clean-point-cloud/yenicikti/20260601_102025_maps5_9dk",
    summary: "Drone yavaşlatıldı, RTAB-Map ayarları ve rota iyileştirildi. Güçlü bir nokta bulutu çıktı.",
    stats: { poses: 156, links: 480, raw: 1723383, voxel: 904960, db: "939 MB" },
    notes: [
      "Yavaş hareketin harita kalitesini artırdığı görüldü.",
      "Final sunum için güçlü karşılaştırma çıktısı.",
      "Eksik kalan bölgeler için sonraki sürümlerde kamera ve otonomi denendi.",
    ],
  },
  {
    id: "maps6",
    name: "Maps6",
    title: "Çoklu Depth Kamera Füzyonu",
    label: "RGB-D",
    quality: "ok",
    period: "9 dk",
    run: "../experiment-archive/06-side-depth-cameras/yenicikti/20260601_110206_maps6_9dk",
    summary: "Sağ ve sol depth kameralar eklendi. Yan depth cloud'ları LiDAR ile birleştirilerek RTAB-Map'e verildi.",
    stats: { poses: 131, links: 402, raw: 1459850, voxel: 841315, db: "669 MB" },
    notes: [
      "Front, left ve right RGB-D snapshotları üretildi.",
      "RTAB-Map çoklu RGB-D doğrudan desteklemediği için merged scan cloud yolu kullanıldı.",
      "Kamera eklemek tek başına mesh kalitesini garanti etmedi.",
    ],
  },
  {
    id: "maps7",
    name: "Maps7",
    title: "Coverage Rota İyileştirme",
    label: "Final",
    quality: "ok",
    period: "9 dk",
    run: "../experiment-archive/07-autonomous-coverage/yenicikti/20260601_133343_maps7_9dk",
    summary: "Coverage rotası ve recovery iyileştirildi. Önceki stuck problemi ciddi şekilde azaldı.",
    stats: { poses: 157, links: 447, raw: 1483804, voxel: 977665, db: "856 MB" },
    notes: [
      "62 hedefin tamamı işlendi; sadece 1 ilerleme problemi kaldı.",
      "Maps serisindeki en yüksek voxel nokta sayısı burada.",
      "Harita dengeli, final sunum için en güçlü adaylardan biri.",
    ],
  },
  {
    id: "maps8",
    name: "Maps8",
    title: "Waypoint'siz Otonom Keşif",
    label: "Otonom",
    quality: "warn",
    period: "9 dk",
    run: "../experiment-archive/08-waypoint-free-coverage/yenicikti/20260601_140218_maps8_9dk",
    summary: "Sabit waypoint listesi kaldırıldı. Drone visited-grid, wall-band, lidar açıklığı ve recovery skorlarıyla yön seçti.",
    stats: { poses: 172, links: 561, raw: 1686127, voxel: 906051, db: "1.07 GB", coverage: "55.1%" },
    notes: [
      "Waypoint listesi yok; hareket yönü anlık skor fonksiyonuyla seçildi.",
      "Yan bantlara Maps7'ye göre daha bilinçli yöneldi.",
      "Tam profesyonel frontier planner değil; ama gerçek otonom coverage mantığını gösteriyor.",
    ],
  },
  {
    id: "maps9",
    name: "Maps9",
    title: "Desenli Tünel Waypoint Keşfi",
    label: "Deneysel",
    quality: "warn",
    period: "10 dk",
    run: "../experiment-archive/09-controlled-tunnel/yenicikti/20260607_200022_maps9_pattern_tunnel_10dk",
    summary: "Sağa sola dönen desenli tünelde yavaş waypoint keşfi. Çıktı alındı fakat bazı waypoint skip ve loop closure problemleri kaldı.",
    stats: { poses: 110, links: 263, raw: 1660820, voxel: 614013, db: "397 MB" },
    assets: {
      bev: "../experiment-archive/09-controlled-tunnel/yenicikti/20260607_200022_maps9_pattern_tunnel_10dk/live_snapshot/fused_slam/cloud_map_top_preview.png",
      side: "",
      ply: "../experiment-archive/09-controlled-tunnel/yenicikti/20260607_200022_maps9_pattern_tunnel_10dk/live_snapshot/fused_slam/cloud_map_snapshot.ply",
      rawPly: "../experiment-archive/09-controlled-tunnel/yenicikti/20260607_200022_maps9_pattern_tunnel_10dk/live_snapshot/fused_slam/cloud_map_snapshot.ply",
      meshObj: "",
      meshPreviewObj: "",
      meshMtl: "",
      meshGlb: "",
      meshPng: "",
      db: "../experiment-archive/09-controlled-tunnel/yenicikti/20260607_200022_maps9_pattern_tunnel_10dk/live_snapshot/fused_slam/rtabmap_live.db",
      front: "../experiment-archive/09-controlled-tunnel/yenicikti/20260607_200022_maps9_pattern_tunnel_10dk/live_snapshot/camera/front_rgb.png",
      depth: "../experiment-archive/09-controlled-tunnel/yenicikti/20260607_200022_maps9_pattern_tunnel_10dk/live_snapshot/camera/front_depth.png",
      left: "../experiment-archive/09-controlled-tunnel/yenicikti/20260607_200022_maps9_pattern_tunnel_10dk/live_snapshot/camera/left_rgb.png",
      right: "../experiment-archive/09-controlled-tunnel/yenicikti/20260607_200022_maps9_pattern_tunnel_10dk/live_snapshot/camera/right_rgb.png",
      lidar: "../experiment-archive/09-controlled-tunnel/yenicikti/20260607_200022_maps9_pattern_tunnel_10dk/live_snapshot/lidar/lidar_top_preview.png",
      fused: "../experiment-archive/09-controlled-tunnel/yenicikti/20260607_200022_maps9_pattern_tunnel_10dk/live_snapshot/fused_slam/cloud_map_top_preview.png",
    },
    notes: [
      "Desenli ve dönüşlü tünel ortamında çıktı alındı.",
      "Bazı waypoint skip ve loop closure problemleri kaldı.",
      "Maps10 için daha geniş dönüş koridoru ve obstacle-aware planner ihtiyacı görüldü.",
    ],
  },
  {
    id: "maps10",
    name: "Maps10",
    title: "Genel Otonom Keşif / Yeni Harita",
    label: "Genel",
    quality: "ok",
    period: "9 dk",
    run: "../experiment-archive/10-general-autonomous/yenicikti/20260621_182940_maps10_general_9dk",
    summary: "Haritaya özel waypoint yazmadan çalışan genel otonom keşif algoritmasıyla yeni oda/koridor ortamında kayıt alındı.",
    stats: { poses: 166, links: 391, raw: 1281401, voxel: 1032035, db: "577 MB" },
    assets: {
      bev: "../experiment-archive/10-general-autonomous/yenicikti/20260621_182940_maps10_general_9dk/live_snapshot/fused_slam/cloud_map_top_preview.png",
      side: "",
      ply: "../experiment-archive/10-general-autonomous/yenicikti/20260621_182940_maps10_general_9dk/rtabmap_export/rtabmap_cloud.ply",
      rawPly: "../experiment-archive/10-general-autonomous/yenicikti/20260621_182940_maps10_general_9dk/rtabmap_export/rtabmap_cloud.ply",
      meshObj: "../experiment-archive/10-general-autonomous/yenicikti/20260621_182940_maps10_general_9dk/rtabmap_export/mesh.obj",
      meshPreviewObj: "",
      meshMtl: "../experiment-archive/10-general-autonomous/yenicikti/20260621_182940_maps10_general_9dk/rtabmap_export/mesh.mtl",
      meshGlb: "../experiment-archive/10-general-autonomous/yenicikti/20260621_182940_maps10_general_9dk/rtabmap_export/mesh_unlit.glb",
      meshPng: "../experiment-archive/10-general-autonomous/yenicikti/20260621_182940_maps10_general_9dk/rtabmap_export/mesh.png",
      db: "../experiment-archive/10-general-autonomous/yenicikti/20260621_182940_maps10_general_9dk/rtabmap_export/rtabmap.db",
      front: "../experiment-archive/10-general-autonomous/yenicikti/20260621_182940_maps10_general_9dk/live_snapshot/camera/front_rgb.png",
      depth: "../experiment-archive/10-general-autonomous/yenicikti/20260621_182940_maps10_general_9dk/live_snapshot/camera/front_depth.png",
      left: "../experiment-archive/10-general-autonomous/yenicikti/20260621_182940_maps10_general_9dk/live_snapshot/camera/left_rgb.png",
      right: "../experiment-archive/10-general-autonomous/yenicikti/20260621_182940_maps10_general_9dk/live_snapshot/camera/right_rgb.png",
      lidar: "../experiment-archive/10-general-autonomous/yenicikti/20260621_182940_maps10_general_9dk/live_snapshot/lidar/lidar_top_preview.png",
      fused: "../experiment-archive/10-general-autonomous/yenicikti/20260621_182940_maps10_general_9dk/live_snapshot/fused_slam/cloud_map_top_preview.png",
    },
    notes: [
      "Haritaya özel rota yazılmadı; Maps10 genel otonom keşif algoritmasıyla çalıştı.",
      "RTAB-Map export sonucunda 1.03 milyon voxel noktalı cloud üretildi.",
      "CloudCompare mesh çıktısı web için GLB/OBJ bağlantılarıyla eklendi.",
    ],
  },
  {
    id: "maps11",
    name: "Maps11",
    title: "Zorlu Dönüşlü Tünel",
    label: "Tünel",
    quality: "ok",
    period: "9 dk",
    run: "../experiment-archive/11-turning-tunnel/yenicikti/20260621_184107_maps11_tunnel_9dk",
    summary: "Sağa sola dönen zorlu tünel ortamında aynı genel otonom keşif sistemiyle SLAM ve mesh çıktısı alındı.",
    stats: { poses: 152, links: 443, raw: 1133121, voxel: 599763, db: "450 MB" },
    assets: {
      bev: "../experiment-archive/11-turning-tunnel/yenicikti/20260621_184107_maps11_tunnel_9dk/rtabmap_export/render_bev.png",
      side: "",
      ply: "../experiment-archive/11-turning-tunnel/yenicikti/20260621_184107_maps11_tunnel_9dk/rtabmap_export/rtabmap_cloud.ply",
      rawPly: "../experiment-archive/11-turning-tunnel/yenicikti/20260621_184107_maps11_tunnel_9dk/rtabmap_export/rtabmap_cloud.ply",
      meshObj: "../experiment-archive/11-turning-tunnel/yenicikti/20260621_184107_maps11_tunnel_9dk/rtabmap_export/mesh.obj",
      meshPreviewObj: "",
      meshMtl: "../experiment-archive/11-turning-tunnel/yenicikti/20260621_184107_maps11_tunnel_9dk/rtabmap_export/mesh.mtl",
      meshGlb: "../experiment-archive/11-turning-tunnel/yenicikti/20260621_184107_maps11_tunnel_9dk/rtabmap_export/mesh_unlit.glb",
      meshPng: "../experiment-archive/11-turning-tunnel/yenicikti/20260621_184107_maps11_tunnel_9dk/rtabmap_export/mesh.png",
      db: "../experiment-archive/11-turning-tunnel/yenicikti/20260621_184107_maps11_tunnel_9dk/rtabmap_export/rtabmap.db",
      front: "../experiment-archive/11-turning-tunnel/yenicikti/20260621_184107_maps11_tunnel_9dk/live_snapshot/camera/front_rgb.png",
      depth: "../experiment-archive/11-turning-tunnel/yenicikti/20260621_184107_maps11_tunnel_9dk/live_snapshot/camera/front_depth.png",
      left: "../experiment-archive/11-turning-tunnel/yenicikti/20260621_184107_maps11_tunnel_9dk/live_snapshot/camera/left_rgb.png",
      right: "../experiment-archive/11-turning-tunnel/yenicikti/20260621_184107_maps11_tunnel_9dk/live_snapshot/camera/right_rgb.png",
      lidar: "../experiment-archive/11-turning-tunnel/yenicikti/20260621_184107_maps11_tunnel_9dk/live_snapshot/lidar/lidar_top_preview.png",
      fused: "../experiment-archive/11-turning-tunnel/yenicikti/20260621_184107_maps11_tunnel_9dk/live_snapshot/fused_slam/cloud_map_top_preview.png",
    },
    notes: [
      "Maps10 ile aynı genel otonom algoritma kullanıldı; haritaya özel rota yazılmadı.",
      "Dönüşlü tünel ve dar geçişler sistemin daha zorlandığı senaryo olarak eklendi.",
      "CloudCompare mesh çıktısı webde önizleme ve dosya bağlantılarıyla sunuluyor.",
    ],
  },
  {
    id: "maps12",
    name: "Maps12",
    title: "Genel SLAM Benchmark Haritası",
    label: "Benchmark",
    quality: "ok",
    period: "9 dk",
    run: "../final-benchmark-experiment/yenicikti/20260621_202718_maps12_general_benchmark_9dk",
    summary: "Odalar, loop koridor, dar geçişler, kolonlar, kutular ve ağaç benzeri engeller içeren farklı benchmark haritasında aynı genel otonom algoritma test edildi.",
    stats: { poses: 151, links: 373, raw: 1498090, voxel: 845870, db: "584 MB" },
    assets: {
      bev: "../final-benchmark-experiment/yenicikti/20260621_202718_maps12_general_benchmark_9dk/rtabmap_export/render_bev.png",
      side: "",
      ply: "../final-benchmark-experiment/yenicikti/20260621_202718_maps12_general_benchmark_9dk/rtabmap_export/rtabmap_cloud.ply",
      rawPly: "../final-benchmark-experiment/yenicikti/20260621_202718_maps12_general_benchmark_9dk/rtabmap_export/rtabmap_cloud.ply",
      meshObj: "../final-benchmark-experiment/yenicikti/20260621_202718_maps12_general_benchmark_9dk/rtabmap_export/mesh.obj",
      meshPreviewObj: "",
      meshMtl: "../final-benchmark-experiment/yenicikti/20260621_202718_maps12_general_benchmark_9dk/rtabmap_export/mesh.mtl",
      meshGlb: "../final-benchmark-experiment/yenicikti/20260621_202718_maps12_general_benchmark_9dk/rtabmap_export/mesh_unlit.glb",
      meshPng: "../final-benchmark-experiment/yenicikti/20260621_202718_maps12_general_benchmark_9dk/rtabmap_export/mesh.png",
      db: "../final-benchmark-experiment/yenicikti/20260621_202718_maps12_general_benchmark_9dk/rtabmap_export/rtabmap.db",
      front: "../final-benchmark-experiment/yenicikti/20260621_202718_maps12_general_benchmark_9dk/live_snapshot/camera/front_rgb.png",
      depth: "../final-benchmark-experiment/yenicikti/20260621_202718_maps12_general_benchmark_9dk/live_snapshot/camera/front_depth.png",
      left: "../final-benchmark-experiment/yenicikti/20260621_202718_maps12_general_benchmark_9dk/live_snapshot/camera/left_rgb.png",
      right: "../final-benchmark-experiment/yenicikti/20260621_202718_maps12_general_benchmark_9dk/live_snapshot/camera/right_rgb.png",
      lidar: "../final-benchmark-experiment/yenicikti/20260621_202718_maps12_general_benchmark_9dk/live_snapshot/lidar/lidar_top_preview.png",
      fused: "../final-benchmark-experiment/yenicikti/20260621_202718_maps12_general_benchmark_9dk/live_snapshot/fused_slam/cloud_map_top_preview.png",
    },
    notes: [
      "experiment-archive/10-general-autonomous/11 ile aynı genel otonom algoritma kullanıldı; haritaya özel rota yazılmadı.",
      "Genel SLAM testlerine benzeyen loop oda/koridor düzeninde denendi.",
      "CloudCompare mesh çıktısı web için GLB/OBJ bağlantılarıyla eklendi.",
    ],
  },
];

for (const map of maps) {
  if (!map.assets) {
    map.assets = {
      bev: `${map.run}/rtabmap_export/render_bev.png`,
      side: `${map.run}/rtabmap_export/render_side.png`,
      ply: `${map.run}/rtabmap_export/rtabmap_cloud_clean_xyzrgb.ply`,
      rawPly: `${map.run}/rtabmap_export/rtabmap_cloud.ply`,
      meshObj: `${map.run}/rtabmap_export/mesh.obj`,
      meshPreviewObj: `${map.run}/rtabmap_export/mesh_preview_textured.obj`,
      meshMtl: `${map.run}/rtabmap_export/mesh.mtl`,
      meshGlb: `${map.run}/rtabmap_export/mesh_unlit.glb`,
      meshPng: `${map.run}/rtabmap_export/mesh.png`,
      db: `${map.run}/rtabmap_export/rtabmap.db`,
      front: `${map.run}/live_snapshot/camera/front_rgb.png`,
      depth: `${map.run}/live_snapshot/camera/front_depth.png`,
      left: `${map.run}/live_snapshot/camera/left_rgb.png`,
      right: `${map.run}/live_snapshot/camera/right_rgb.png`,
      lidar: `${map.run}/live_snapshot/lidar/lidar_top_preview.png`,
      fused: `${map.run}/live_snapshot/fused_slam/cloud_map_top_preview.png`,
    };
  }
}

for (const id of ["maps3", "maps8"]) {
  const map = maps.find((item) => item.id === id);
  if (map?.assets) {
    map.assets.meshObj = "";
    map.assets.meshPreviewObj = "";
    map.assets.meshMtl = "";
    map.assets.meshGlb = "";
    map.assets.meshPng = "";
  }
}

for (const id of ["maps2", "maps4", "maps5", "maps6"]) {
  const map = maps.find((item) => item.id === id);
  if (map?.assets) {
    map.assets.meshGlb = "";
  }
}

const $ = (selector) => document.querySelector(selector);
const fmt = (value) => (typeof value === "number" ? value.toLocaleString("tr-TR") : value || "-");
const img = (src, alt) =>
  src ? `<img src="${src}" alt="${alt}" loading="lazy" onerror="this.closest('.media-box')?.remove(); this.remove()">` : "";

function mediaBox(src, alt, label) {
  return src ? `<div class="media-box">${img(src, alt)}<strong>${label}</strong></div>` : "";
}

function meshBox(map) {
  if (!map.assets.meshPng) {
    return `<div class="mesh-placeholder">
      <strong>Mesh çıktısı henüz eklenmedi</strong>
      <span>Bu senaryo için ` + "rtabmap_export/mesh.obj" + ` üretildiğinde burada görünecek.</span>
    </div>`;
  }
  return `<div class="mesh-preview">
    <img src="${map.assets.meshPng}" alt="${map.name} mesh önizleme" loading="lazy">
    <div>
      <strong>RTAB-Map Mesh Önizleme</strong>
      <span>OBJ dosyası ayrı olarak açılabilir. Web sayfasında ağır yük bindirmemek için PNG önizleme gösteriliyor.</span>
    </div>
  </div>`;
}

function meshViewerBox(map) {
  if (!map.assets.meshGlb && !map.assets.meshPreviewObj && !map.assets.meshObj) return "";
  return `<div class="mesh-viewer-stage">
    <div id="meshViewer" style="--mesh-fallback: url('${map.assets.meshPng || map.assets.bev || map.assets.fused || ""}')"></div>
    <div id="meshStatus" class="viewer-status">CloudCompare kalitesine yakın 3B mesh için butona bas.</div>
  </div>`;
}

function emptyMedia(message) {
  return `<div class="empty-media">${message}</div>`;
}

function badge(map) {
  const klass = map.quality === "ok" ? "" : map.quality === "bad" ? "bad" : "warn";
  return `<span class="badge ${klass}">${map.label}</span>`;
}

function stat(label, value) {
  return `<div class="metric"><span>${label}</span><strong>${fmt(value)}</strong></div>`;
}

function fileLink(label, href, hint) {
  if (!href) return "";
  return `<a href="${href}" target="_blank" rel="noreferrer"><span>${hint}</span><strong>${label}</strong></a>`;
}

function renderNav(activeId) {
  $("#mapNav").innerHTML = maps
    .map((map) => `<a class="${map.id === activeId ? "active" : ""}" href="#${map.id}">${map.name}</a>`)
    .join("");
}

function renderHome() {
  renderNav("");
  $("#detailView").hidden = true;
  $("#homeView").hidden = false;
  $("#mapGrid").innerHTML = maps
    .map(
      (map) => `
      <a class="map-card" href="#${map.id}">
        <img src="${map.assets.bev || map.assets.fused}" alt="${map.name} ana harita görüntüsü" loading="lazy">
        <div class="map-card-body">
          <div class="map-card-header">
            <div>
              <h2>${map.name}</h2>
              <strong>${map.title}</strong>
            </div>
            ${badge(map)}
          </div>
          <p>${map.summary}</p>
        </div>
      </a>
    `,
    )
    .join("");
  window.scrollTo({ top: 0, behavior: "instant" });
}

function renderDetail(map, targetSection = "") {
  resetViewer();
  renderNav(map.id);
  $("#homeView").hidden = true;
  $("#detailView").hidden = false;
  $("#detailJumpNav").innerHTML = [
    ["final", "Final çıktı"],
    ["viewer", "3B"],
    ["camera", "Kamera"],
    ["sensor", "LiDAR/Füzyon"],
    ["files", "Dosyalar"],
  ]
    .map(([id, label]) => `<a href="#${map.id}-${id}" data-jump="${map.id}-${id}">${label}</a>`)
    .join("");

  const finalMedia = [
    mediaBox(map.assets.bev || map.assets.fused, `${map.name} BEV`, "BEV / Kuş bakışı harita"),
    mediaBox(map.assets.side, `${map.name} yan görünüm`, "Yan görünüm"),
  ].filter(Boolean).join("") || emptyMedia("Bu map için final PNG çıktısı bulunamadı.");

  const cameraMedia = [
    mediaBox(map.assets.front, `${map.name} front rgb`, "Front RGB"),
    mediaBox(map.assets.depth, `${map.name} front depth`, "Front Depth"),
    mediaBox(map.assets.left, `${map.name} left rgb`, "Left RGB"),
    mediaBox(map.assets.right, `${map.name} right rgb`, "Right RGB"),
  ].filter(Boolean).join("") || emptyMedia("Bu map için kamera/depth snapshot çıktısı bulunamadı.");

  const sensorMedia = [
    mediaBox(map.assets.lidar, `${map.name} lidar preview`, "LiDAR top preview"),
    mediaBox(map.assets.fused, `${map.name} fused preview`, "Fused SLAM preview"),
  ].filter(Boolean).join("") || emptyMedia("Bu map için LiDAR/fused preview çıktısı bulunamadı.");

  $("#detailContent").innerHTML = `
    <section class="detail-hero">
      <div class="detail-title" style="background-image: linear-gradient(rgba(31,41,37,.82), rgba(31,41,37,.72)), url('${map.assets.bev || map.assets.fused}')">
        ${badge(map)}
        <h1>${map.name}</h1>
        <p><strong>${map.title}</strong></p>
        <p>${map.summary}</p>
      </div>
      <div class="hero-preview">
        <img src="${map.assets.bev || map.assets.fused}" alt="${map.name} final harita çıktısı">
      </div>
    </section>

    <div class="metric-row">
      ${stat("Süre", map.period)}
      ${stat("Pose", map.stats.poses)}
      ${stat("Link", map.stats.links)}
      ${stat("Voxel Nokta", map.stats.voxel)}
      ${stat("Coverage", map.stats.coverage || "-")}
    </div>

    <section id="${map.id}-final" class="chapter">
      <div class="chapter-header">
        <div>
          <h2>1. Final Harita Çıktısı</h2>
          <p>Sunumda ilk gösterilecek en önemli çıktı: RTAB-Map nokta bulutunun kuş bakışı ve varsa yan görünümü.</p>
        </div>
        <a class="action-link" href="${map.assets.bev || map.assets.fused}" target="_blank" rel="noreferrer">PNG Aç</a>
      </div>
      <div class="image-pair">
        ${finalMedia}
      </div>
    </section>

    <section id="${map.id}-viewer" class="chapter">
      <div class="chapter-header">
        <div>
          <h2>2. 3B Nokta Bulutu</h2>
          <p>PLY dosyasını web içinde döndürerek inceleyebilirsin. Büyük dosyalar birkaç saniye yüklenebilir.</p>
        </div>
        <div class="action-row">
          <button class="primary-button" id="loadPlyButton">3B PLY Yükle</button>
          ${map.assets.ply ? `<a class="action-link" href="${map.assets.ply}" target="_blank" rel="noreferrer">PLY Dosyası</a>` : ""}
        </div>
      </div>
      <div class="viewer-stage" style="--viewer-fallback: url('${map.assets.bev || map.assets.fused || ""}')">
        <div id="plyViewer"></div>
        <div id="viewerStatus" class="viewer-status">3B nokta bulutu otomatik yükleniyor...</div>
      </div>
    </section>

    <section id="${map.id}-camera" class="chapter">
      <div class="chapter-header">
        <div>
          <h2>3. Kamera ve Depth Görüntüleri</h2>
          <p>Drone'un aldığı RGB ve depth görüntüleri. Maps6 sonrası sağ/sol kamera çıktıları da var.</p>
        </div>
      </div>
      <div class="image-grid">
        ${cameraMedia}
      </div>
    </section>

    <section id="${map.id}-sensor" class="chapter">
      <div class="chapter-header">
        <div>
          <h2>4. LiDAR ve Füzyon Önizleme</h2>
          <p>Ham LiDAR önizlemesi ve RTAB-Map/fused SLAM anlık harita görüntüsü.</p>
        </div>
      </div>
      <div class="image-pair">
        ${sensorMedia}
      </div>
    </section>

    <section id="${map.id}-files" class="chapter">
      <div class="chapter-header">
        <div>
          <h2>5. Açılabilir Dosyalar</h2>
          <p>Sunum veya inceleme sırasında doğrudan açılabilecek ana dosyalar.</p>
        </div>
      </div>
      <div class="file-links">
        ${fileLink("RTAB-Map DB", map.assets.db, "Database Viewer")}
        ${fileLink("Temiz PLY", map.assets.ply, "3B nokta bulutu")}
        ${fileLink("Ham PLY", map.assets.rawPly, "Export cloud")}
        ${fileLink("Tam GLB Mesh", map.assets.meshGlb, "CloudCompare'e yakın web modeli")}
        ${fileLink("Texture'lı Web Mesh", map.assets.meshPreviewObj, "Hafif 3B inceleme")}
        ${fileLink("Mesh OBJ", map.assets.meshObj, "Yüzey modeli")}
        ${fileLink("Mesh PNG", map.assets.meshPng, "Mesh önizleme")}
        ${fileLink("Run klasörü", map.run, "Tüm çıktılar")}
      </div>
    </section>
  `;

  $("#loadPlyButton")?.addEventListener("click", () => loadPly(map));
  if (map.assets.ply) {
    setTimeout(() => loadPly(map), 250);
  } else {
    $("#viewerStatus").textContent = "Bu senaryo için PLY dosyası bulunamadı.";
  }
  $("#detailJumpNav").querySelectorAll("[data-jump]").forEach((link) => {
    link.addEventListener("click", (event) => {
      event.preventDefault();
      document.getElementById(link.dataset.jump)?.scrollIntoView({ behavior: "smooth", block: "start" });
      history.replaceState(null, "", `#${map.id}`);
    });
  });
  if (targetSection) {
    setTimeout(() => {
      document.getElementById(targetSection)?.scrollIntoView({ behavior: "instant", block: "start" });
    }, 100);
  } else {
    window.scrollTo({ top: 0, behavior: "instant" });
  }
}

$("#backHome").addEventListener("click", () => {
  history.pushState("", document.title, window.location.pathname);
  renderHome();
});

function route() {
  const hash = window.location.hash.replace("#", "");
  const id = hash.split("-")[0];
  const map = maps.find((item) => item.id === id);
  if (map) renderDetail(map, hash.includes("-") ? hash : "");
  else renderHome();
}

let renderer;
let scene;
let camera;
let controls;
let currentPoints;
let THREE;
let OrbitControls;
let OBJLoader;
let MTLLoader;
let GLTFLoader;
let viewerReady = false;
let animationId;
let meshRenderer;
let meshScene;
let meshCamera;
let meshControls;
let meshObject;
let meshViewerReady = false;
let meshAnimationId;

function resetViewer() {
  if (animationId) {
    cancelAnimationFrame(animationId);
    animationId = undefined;
  }
  if (currentPoints && scene) {
    scene.remove(currentPoints);
    currentPoints.geometry?.dispose();
    currentPoints.material?.dispose();
  }
  renderer?.dispose?.();
  renderer = undefined;
  scene = undefined;
  camera = undefined;
  controls = undefined;
  currentPoints = undefined;
  viewerReady = false;

  if (meshAnimationId) {
    cancelAnimationFrame(meshAnimationId);
    meshAnimationId = undefined;
  }
  if (meshObject && meshScene) {
    meshScene.remove(meshObject);
    meshObject.traverse?.((child) => {
      child.geometry?.dispose?.();
      child.material?.dispose?.();
    });
  }
  meshRenderer?.dispose?.();
  meshRenderer = undefined;
  meshScene = undefined;
  meshCamera = undefined;
  meshControls = undefined;
  meshObject = undefined;
  meshViewerReady = false;
}

async function ensureViewer() {
  if (viewerReady) return true;
  const status = $("#viewerStatus");
  status.textContent = "3B motor yükleniyor...";
  try {
    THREE = await import("./node_modules/three/build/three.module.js");
    ({ OrbitControls } = await import("./node_modules/three/examples/jsm/controls/OrbitControls.js"));
  } catch (error) {
    status.textContent = `3B motor yüklenemedi: ${error.message}`;
    return false;
  }

  const stage = $("#plyViewer");
  const width = stage.clientWidth || 920;
  const height = stage.clientHeight || 620;
  scene = new THREE.Scene();
  scene.background = new THREE.Color(0x101513);
  camera = new THREE.PerspectiveCamera(55, width / height, 0.01, 1000);
  camera.position.set(0, -16, 10);
  renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.setSize(width, height);
  stage.innerHTML = "";
  stage.classList.add("loading");
  stage.appendChild(renderer.domElement);
  controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.target.set(0, 0, 1);

  const grid = new THREE.GridHelper(20, 20, 0x4d655d, 0x26302c);
  grid.rotation.x = Math.PI / 2;
  scene.add(grid);

  window.addEventListener("resize", () => {
    const currentStage = $("#plyViewer");
    if (!currentStage || !renderer) return;
    const nextWidth = currentStage.clientWidth || 920;
    const nextHeight = currentStage.clientHeight || 620;
    camera.aspect = nextWidth / nextHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(nextWidth, nextHeight);
  });

  animate();
  viewerReady = true;
  return true;
}

function animate() {
  animationId = requestAnimationFrame(animate);
  controls?.update();
  renderer?.render(scene, camera);
}

async function ensureMeshViewer() {
  if (meshViewerReady) return true;
  const status = $("#meshStatus");
  if (!status) return false;
  status.textContent = "3B mesh motor yükleniyor...";
  try {
    THREE = THREE || (await import("./node_modules/three/build/three.module.js"));
    if (!OrbitControls) {
      ({ OrbitControls } = await import("./node_modules/three/examples/jsm/controls/OrbitControls.js"));
    }
    ({ OBJLoader } = await import("./node_modules/three/examples/jsm/loaders/OBJLoader.js"));
    ({ MTLLoader } = await import("./node_modules/three/examples/jsm/loaders/MTLLoader.js"));
    ({ GLTFLoader } = await import("./node_modules/three/examples/jsm/loaders/GLTFLoader.js"));
  } catch (error) {
    status.textContent = `3B mesh motor yüklenemedi: ${error.message}`;
    return false;
  }

  const stage = $("#meshViewer");
  const width = stage.clientWidth || 920;
  const height = stage.clientHeight || 620;
  meshScene = new THREE.Scene();
  meshScene.background = new THREE.Color(0x101513);
  meshCamera = new THREE.PerspectiveCamera(50, width / height, 0.01, 1000);
  meshCamera.position.set(0, -12, 8);
  meshRenderer = new THREE.WebGLRenderer({ antialias: true });
  meshRenderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  meshRenderer.setSize(width, height);
  stage.innerHTML = "";
  stage.classList.add("loading");
  stage.appendChild(meshRenderer.domElement);

  meshControls = new OrbitControls(meshCamera, meshRenderer.domElement);
  meshControls.enableDamping = true;

  const hemi = new THREE.HemisphereLight(0xffffff, 0x2f3a36, 1.8);
  meshScene.add(hemi);
  const dir = new THREE.DirectionalLight(0xffffff, 1.6);
  dir.position.set(3, -5, 8);
  meshScene.add(dir);
  const grid = new THREE.GridHelper(20, 20, 0x4d655d, 0x26302c);
  grid.rotation.x = Math.PI / 2;
  meshScene.add(grid);

  window.addEventListener("resize", () => {
    const currentStage = $("#meshViewer");
    if (!currentStage || !meshRenderer) return;
    const nextWidth = currentStage.clientWidth || 920;
    const nextHeight = currentStage.clientHeight || 620;
    meshCamera.aspect = nextWidth / nextHeight;
    meshCamera.updateProjectionMatrix();
    meshRenderer.setSize(nextWidth, nextHeight);
  });

  animateMesh();
  meshViewerReady = true;
  return true;
}

function animateMesh() {
  meshAnimationId = requestAnimationFrame(animateMesh);
  meshControls?.update();
  meshRenderer?.render(meshScene, meshCamera);
}

function parsePly(buffer) {
  const bytes = new Uint8Array(buffer);
  const marker = new TextEncoder().encode("end_header\n");
  let headerEnd = -1;
  for (let i = 0; i <= bytes.length - marker.length; i += 1) {
    let ok = true;
    for (let j = 0; j < marker.length; j += 1) {
      if (bytes[i + j] !== marker[j]) {
        ok = false;
        break;
      }
    }
    if (ok) {
      headerEnd = i + marker.length;
      break;
    }
  }
  if (headerEnd < 0) throw new Error("PLY header bulunamadı.");
  const header = new TextDecoder().decode(bytes.slice(0, headerEnd));
  const vertexLine = header.split("\n").find((line) => line.startsWith("element vertex"));
  const count = Number(vertexLine?.split(/\s+/).at(-1));
  const props = [];
  let inVertex = false;
  for (const line of header.split("\n")) {
    if (line.startsWith("element vertex")) {
      inVertex = true;
      continue;
    }
    if (inVertex && line.startsWith("element ")) break;
    if (inVertex && line.startsWith("property")) props.push(line.trim().split(/\s+/));
  }
  const sizes = props.map((p) => (p[1].includes("float") || p[1].includes("int") ? 4 : 1));
  const stride = sizes.reduce((a, b) => a + b, 0);
  const offsets = {};
  let offset = 0;
  props.forEach((p, index) => {
    offsets[p[2]] = offset;
    offset += sizes[index];
  });

  const view = new DataView(buffer, headerEnd);
  const positions = new Float32Array(count * 3);
  const colors = new Float32Array(count * 3);
  const hasRgb = offsets.red !== undefined && offsets.green !== undefined && offsets.blue !== undefined;

  for (let i = 0; i < count; i += 1) {
    const base = i * stride;
    positions[i * 3] = view.getFloat32(base + offsets.x, true);
    positions[i * 3 + 1] = view.getFloat32(base + offsets.y, true);
    positions[i * 3 + 2] = view.getFloat32(base + offsets.z, true);
    colors[i * 3] = hasRgb ? Math.max(view.getUint8(base + offsets.red) / 255, 0.18) : 0.25;
    colors[i * 3 + 1] = hasRgb ? Math.max(view.getUint8(base + offsets.green) / 255, 0.18) : 0.65;
    colors[i * 3 + 2] = hasRgb ? Math.max(view.getUint8(base + offsets.blue) / 255, 0.18) : 0.9;
  }
  return { positions, colors, count };
}

async function loadPly(map) {
  if (!map.assets.ply) return;
  const ready = await ensureViewer();
  if (!ready) return;
  const status = $("#viewerStatus");
  status.textContent = `${map.name} PLY yükleniyor...`;
  try {
    const response = await fetch(map.assets.ply);
    if (!response.ok) throw new Error(`${response.status} ${response.statusText}`);
    const parsed = parsePly(await response.arrayBuffer());
    if (currentPoints) {
      scene.remove(currentPoints);
      currentPoints.geometry.dispose();
      currentPoints.material.dispose();
    }
    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute("position", new THREE.BufferAttribute(parsed.positions, 3));
    geometry.setAttribute("color", new THREE.BufferAttribute(parsed.colors, 3));
    geometry.computeBoundingBox();
    const material = new THREE.PointsMaterial({ size: 0.06, vertexColors: true, sizeAttenuation: true });
    currentPoints = new THREE.Points(geometry, material);
    scene.add(currentPoints);
    $("#plyViewer")?.classList.add("loaded");
    const center = new THREE.Vector3();
    geometry.boundingBox.getCenter(center);
    controls.target.copy(center);
    camera.position.set(center.x, center.y - 16, center.z + 10);
    controls.update();
    status.textContent = `${map.name}: ${fmt(parsed.count)} nokta yüklendi.`;
  } catch (error) {
    status.textContent = `PLY yüklenemedi: ${error.message}`;
  }
}

async function loadMesh(map) {
  if (!map.assets.meshGlb && !map.assets.meshPreviewObj && !map.assets.meshObj) return;
  const ready = await ensureMeshViewer();
  if (!ready) return;
  const status = $("#meshStatus");
  const source = map.assets.meshGlb || map.assets.meshPreviewObj || map.assets.meshObj;
  status.textContent = `${map.name} mesh yükleniyor... Büyük GLB dosyasında bu işlem biraz sürebilir.`;
  try {
    let object;
    if (map.assets.meshGlb) {
      const loader = new GLTFLoader();
      const gltf = await new Promise((resolve, reject) => {
        loader.load(
          map.assets.meshGlb,
          resolve,
          (event) => {
            if (event.total) {
              const percent = Math.round((event.loaded / event.total) * 100);
              status.textContent = `${map.name} GLB indiriliyor: %${percent}. Dosya büyük olduğu için biraz bekle.`;
            } else {
              status.textContent = `${map.name} GLB indiriliyor: ${Math.round(event.loaded / 1024 / 1024)} MB alındı.`;
            }
          },
          reject,
        );
      });
      object = gltf.scene;
    } else {
      const loader = new OBJLoader();
      if (map.assets.meshMtl) {
      const resourcePath = map.assets.meshMtl.slice(0, map.assets.meshMtl.lastIndexOf("/") + 1);
      const mtlLoader = new MTLLoader();
      mtlLoader.setResourcePath(resourcePath);
      mtlLoader.setPath(resourcePath);
      const materials = await mtlLoader.loadAsync("mesh.mtl");
      materials.preload();
      loader.setMaterials(materials);
      }
      object = await loader.loadAsync(source);
    }
    if (meshObject) {
      meshScene.remove(meshObject);
      meshObject.traverse?.((child) => {
        child.geometry?.dispose?.();
        child.material?.dispose?.();
      });
    }
    object.traverse((child) => {
      if (child.isMesh) {
        if (Array.isArray(child.material)) {
          child.material.forEach((material) => {
            material.side = THREE.DoubleSide;
            material.needsUpdate = true;
          });
        } else if (child.material) {
          child.material.side = THREE.DoubleSide;
          child.material.needsUpdate = true;
        } else {
          child.material = new THREE.MeshStandardMaterial({
            color: 0x8fd3c7,
            roughness: 0.8,
            metalness: 0.02,
            side: THREE.DoubleSide,
          });
        }
        child.geometry.computeVertexNormals?.();
      }
    });
    meshScene.add(object);
    meshObject = object;

    const box = new THREE.Box3().setFromObject(object);
    const center = new THREE.Vector3();
    const size = new THREE.Vector3();
    box.getCenter(center);
    box.getSize(size);
    meshControls.target.copy(center);
    const distance = Math.max(size.x, size.y, size.z, 1) * 1.35;
    meshCamera.position.set(center.x, center.y - distance, center.z + distance * 0.62);
    meshCamera.near = Math.max(distance / 1000, 0.01);
    meshCamera.far = Math.max(distance * 8, 100);
    meshCamera.updateProjectionMatrix();
    meshControls.update();
    $("#meshViewer")?.classList.add("loaded");
    status.textContent = map.assets.meshGlb
      ? `${map.name}: tam texture'lı GLB mesh yüklendi. Bu, CloudCompare görüntüsüne en yakın web sürümüdür.`
      : `${map.name}: texture'lı web preview yüklendi. Tam OBJ dosyası CloudCompare için ayrıca duruyor.`;
  } catch (error) {
    status.textContent = `Mesh yüklenemedi: ${error.message}`;
  }
}

window.addEventListener("hashchange", route);
route();
