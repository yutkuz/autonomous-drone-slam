using DroneSlam.Application.DTOs;
using DroneSlam.Application.Interfaces;
using DroneSlam.Application.Options;
using DroneSlam.Domain.Entities;
using Microsoft.Extensions.Options;

namespace DroneSlam.Infrastructure.Services;

public sealed class ProjectFinalImportService(
    IMapRunRepository repository,
    IOptions<ProjectFinalOptions> options) : IMapImportService
{
    private readonly ProjectFinalOptions _options = options.Value;

    public async Task<ImportResultDto> ImportProjectFinalAsync(CancellationToken cancellationToken)
    {
        var root = Path.GetFullPath(_options.RootPath);
        var maps = Directory.Exists(root)
            ? Directory.GetDirectories(root, "Maps*", SearchOption.TopDirectoryOnly)
                .Select(path => BuildMapRun(root, path))
                .Where(map => map is not null)
                .Cast<MapRun>()
                .OrderBy(map => map.MapKey.Length)
                .ThenBy(map => map.MapKey)
                .ToList()
            : [];

        await repository.UpsertRangeAsync(maps, cancellationToken);
        return new ImportResultDto(maps.Count, maps.Sum(x => x.Assets.Count), DateTimeOffset.UtcNow);
    }

    private static MapRun? BuildMapRun(string root, string mapDirectory)
    {
        var mapKey = Path.GetFileName(mapDirectory).ToLowerInvariant();
        if (!mapKey.StartsWith("maps", StringComparison.OrdinalIgnoreCase)) return null;

        var metadata = MapCatalog.Get(mapKey);
        var runDirectory = FindBestRunDirectory(mapDirectory);
        if (runDirectory is null) return null;

        var map = new MapRun
        {
            Id = Guid.NewGuid(),
            MapKey = mapKey,
            Name = metadata.Name,
            Title = metadata.Title,
            Label = metadata.Label,
            Quality = metadata.Quality,
            Period = metadata.Period,
            Summary = metadata.Summary,
            AbsoluteRunPath = runDirectory,
            RelativeRunPath = ToRelative(root, runDirectory),
            FlightStartedAt = ParseRunDate(Path.GetFileName(runDirectory)),
            ImportedAt = DateTimeOffset.UtcNow,
            IsAvailable = true
        };

        foreach (var note in metadata.Notes.Select((text, index) => new MapNote
        {
            Id = Guid.NewGuid(),
            MapRunId = map.Id,
            SortOrder = index + 1,
            Text = text
        }))
        {
            map.Notes.Add(note);
        }

        var assets = BuildAssets(root, map.Id, runDirectory);
        foreach (var asset in assets) map.Assets.Add(asset);

        var dbAsset = assets.FirstOrDefault(x => x.AssetType == "db");
        var cleanPly = assets.FirstOrDefault(x => x.AssetType == "ply");
        var rawPly = assets.FirstOrDefault(x => x.AssetType == "rawPly");
        var mesh = assets.FirstOrDefault(x => x.AssetType == "meshObj");

        map.Metric = new MapMetric
        {
            Id = Guid.NewGuid(),
            MapRunId = map.Id,
            PoseCount = metadata.Poses ?? CountLines(FindFile(runDirectory, "rtabmap_export/rtabmap_cloud_poses.txt")),
            LinkCount = metadata.Links,
            RawPointCount = metadata.RawPoints,
            VoxelPointCount = metadata.VoxelPoints ?? ReadPlyVertexCount(cleanPly?.AbsolutePath) ?? ReadPlyVertexCount(rawPly?.AbsolutePath),
            CoveragePercent = metadata.Coverage,
            DatabaseSizeBytes = dbAsset?.SizeBytes,
            PointCloudSizeBytes = cleanPly?.SizeBytes ?? rawPly?.SizeBytes,
            MeshSizeBytes = mesh?.SizeBytes
        };

        return map;
    }

    private static string? FindBestRunDirectory(string mapDirectory)
    {
        var candidates = new List<string>();
        var outputRoot = Path.Combine(mapDirectory, "outputs");
        var newOutputRoot = Path.Combine(mapDirectory, "yenicikti");

        if (Directory.Exists(newOutputRoot))
        {
            candidates.AddRange(Directory.GetDirectories(newOutputRoot));
        }

        if (Directory.Exists(outputRoot))
        {
            var outputChildren = Directory.GetDirectories(outputRoot);
            candidates.AddRange(outputChildren.Length > 0 ? outputChildren : [outputRoot]);
        }

        return candidates
            .Where(HasUsefulMapAsset)
            .OrderByDescending(GetRunDirectoryScore)
            .ThenByDescending(path => Directory.GetLastWriteTimeUtc(path))
            .FirstOrDefault();
    }

    private static bool HasUsefulMapAsset(string directory)
    {
        return File.Exists(Path.Combine(directory, "rtabmap_export/rtabmap.db"))
            || File.Exists(Path.Combine(directory, "rtabmap.db"))
            || File.Exists(Path.Combine(directory, "cloud_map_snapshot.ply"));
    }

    private static int GetRunDirectoryScore(string directory)
    {
        var score = 0;

        if (File.Exists(Path.Combine(directory, "rtabmap_export/render_bev.png"))) score += 100;
        if (File.Exists(Path.Combine(directory, "rtabmap_export/render_side.png"))) score += 25;
        if (File.Exists(Path.Combine(directory, "live_snapshot/fused_slam/cloud_map_top_preview.png"))) score += 40;
        if (File.Exists(Path.Combine(directory, "live_snapshot/camera/front_rgb.png"))) score += 30;
        if (File.Exists(Path.Combine(directory, "live_snapshot/camera/front_depth.png"))) score += 20;
        if (File.Exists(Path.Combine(directory, "live_snapshot/lidar/lidar_top_preview.png"))) score += 20;
        if (File.Exists(Path.Combine(directory, "rtabmap_export/rtabmap_cloud.ply"))) score += 35;
        if (File.Exists(Path.Combine(directory, "cloud_map_snapshot.ply"))) score += 20;
        if (File.Exists(Path.Combine(directory, "rtabmap_export/rtabmap.db"))) score += 15;
        if (File.Exists(Path.Combine(directory, "rtabmap.db"))) score += 5;

        if (directory.Contains($"{Path.DirectorySeparatorChar}yenicikti{Path.DirectorySeparatorChar}", StringComparison.OrdinalIgnoreCase))
        {
            score += 10;
        }

        return score;
    }

    private static IReadOnlyList<MapAsset> BuildAssets(string root, Guid mapRunId, string runDirectory)
    {
        var specs = new (string Type, string DisplayName, string Relative, string ContentType)[]
        {
            ("bev", "BEV / kuş bakışı PNG", "rtabmap_export/render_bev.png", "image/png"),
            ("side", "Yan görünüm PNG", "rtabmap_export/render_side.png", "image/png"),
            ("ply", "Temiz 3B PLY", "rtabmap_export/rtabmap_cloud_clean_xyzrgb.ply", "application/octet-stream"),
            ("rawPly", "Ham RTAB-Map PLY", "rtabmap_export/rtabmap_cloud.ply", "application/octet-stream"),
            ("meshObj", "Mesh OBJ", "rtabmap_export/mesh.obj", "text/plain"),
            ("meshMtl", "Mesh MTL", "rtabmap_export/mesh.mtl", "text/plain"),
            ("meshGlb", "Web GLB Mesh", "rtabmap_export/mesh_unlit.glb", "model/gltf-binary"),
            ("meshPng", "Mesh PNG", "rtabmap_export/mesh.png", "image/png"),
            ("db", "RTAB-Map DB", "rtabmap_export/rtabmap.db", "application/octet-stream"),
            ("front", "Front RGB", "live_snapshot/camera/front_rgb.png", "image/png"),
            ("depth", "Front depth", "live_snapshot/camera/front_depth.png", "image/png"),
            ("left", "Left RGB", "live_snapshot/camera/left_rgb.png", "image/png"),
            ("right", "Right RGB", "live_snapshot/camera/right_rgb.png", "image/png"),
            ("lidar", "LiDAR önizleme", "live_snapshot/lidar/lidar_top_preview.png", "image/png"),
            ("fused", "Fused SLAM önizleme", "live_snapshot/fused_slam/cloud_map_top_preview.png", "image/png"),
            ("run", "Run klasörü", ".", "text/plain")
        };

        var assets = new List<MapAsset>();
        foreach (var spec in specs)
        {
            var absolutePath = ResolveAssetPath(runDirectory, spec.Relative, spec.Type);
            var exists = spec.Type == "run" ? Directory.Exists(absolutePath) : File.Exists(absolutePath);
            var size = exists && File.Exists(absolutePath) ? new FileInfo(absolutePath).Length : 0;

            assets.Add(new MapAsset
            {
                Id = Guid.NewGuid(),
                MapRunId = mapRunId,
                AssetType = spec.Type,
                DisplayName = spec.DisplayName,
                AbsolutePath = absolutePath,
                RelativePath = ToRelative(root, absolutePath),
                ContentType = spec.ContentType,
                SizeBytes = size,
                ExistsOnDisk = exists
            });
        }

        AddFallback(assets, root, mapRunId, runDirectory, "bev", "cloud_map_top_preview.png", "image/png");
        AddFallback(assets, root, mapRunId, runDirectory, "ply", "cloud_map_snapshot.ply", "application/octet-stream");
        AddFallback(assets, root, mapRunId, runDirectory, "db", "rtabmap.db", "application/octet-stream");
        return assets;
    }

    private static void AddFallback(
        List<MapAsset> assets,
        string root,
        Guid mapRunId,
        string runDirectory,
        string type,
        string relative,
        string contentType)
    {
        if (assets.Any(x => x.AssetType == type && x.ExistsOnDisk)) return;

        var absolutePath = Path.Combine(runDirectory, relative);
        if (!File.Exists(absolutePath)) return;

        assets.RemoveAll(x => x.AssetType == type);
        assets.Add(new MapAsset
        {
            Id = Guid.NewGuid(),
            MapRunId = mapRunId,
            AssetType = type,
            DisplayName = type,
            AbsolutePath = absolutePath,
            RelativePath = ToRelative(root, absolutePath),
            ContentType = contentType,
            SizeBytes = new FileInfo(absolutePath).Length,
            ExistsOnDisk = true
        });
    }

    private static string ResolveAssetPath(string runDirectory, string relative, string type)
    {
        if (type == "run") return runDirectory;
        return Path.Combine(runDirectory, relative);
    }

    private static string ToRelative(string root, string path)
    {
        return Path.GetRelativePath(root, path).Replace(Path.DirectorySeparatorChar, '/');
    }

    private static string? FindFile(string root, string relative)
    {
        var path = Path.Combine(root, relative);
        return File.Exists(path) ? path : null;
    }

    private static int? CountLines(string? path)
    {
        if (path is null || !File.Exists(path)) return null;
        var count = File.ReadLines(path).Count(line => !string.IsNullOrWhiteSpace(line) && !line.StartsWith('#'));
        return count > 0 ? count : null;
    }

    private static long? ReadPlyVertexCount(string? path)
    {
        if (path is null || !File.Exists(path)) return null;

        foreach (var line in File.ReadLines(path).Take(80))
        {
            if (!line.StartsWith("element vertex ", StringComparison.OrdinalIgnoreCase)) continue;
            return long.TryParse(line["element vertex ".Length..].Trim(), out var count) ? count : null;
        }

        return null;
    }

    private static DateTimeOffset? ParseRunDate(string name)
    {
        var digits = new string(name.TakeWhile(ch => char.IsDigit(ch) || ch == '_').ToArray()).TrimEnd('_');
        if (DateTimeOffset.TryParseExact(digits, "yyyyMMdd_HHmmss", null, System.Globalization.DateTimeStyles.AssumeLocal, out var date))
        {
            return date;
        }

        return null;
    }

    private sealed record MapMetadata(
        string Name,
        string Title,
        string Label,
        string Quality,
        string Period,
        string Summary,
        int? Poses,
        int? Links,
        long? RawPoints,
        long? VoxelPoints,
        decimal? Coverage,
        IReadOnlyList<string> Notes);

    private static class MapCatalog
    {
        public static MapMetadata Get(string mapKey)
        {
            return Catalog.TryGetValue(mapKey, out var metadata)
                ? metadata
                : new MapMetadata(mapKey.ToUpperInvariant(), "SLAM Koşusu", "Yeni", "warn", "-", "Project-Final klasöründen içe aktarılan deney kaydı.", null, null, null, null, null, ["Proje klasöründen içe aktarıldı."]);
        }

        private static readonly Dictionary<string, MapMetadata> Catalog = new(StringComparer.OrdinalIgnoreCase)
        {
            ["maps1"] = new("Maps1", "Maps1 Başlangıç Çalışması", "Ham", "warn", "manuel", "İlk yüklenen çalışan proje. Sonraki sürümler için referans olarak tutuldu.", null, null, null, null, null, ["Ham çalışan referans proje olarak saklandı.", "RTAB-Map veritabanı ve nokta bulutu mevcut."]),
            ["maps2"] = new("Maps2", "Feature Room Baseline", "Erken", "bad", "4 dk", "RTAB-Map SLAM akışının düzenli çıktı alınan ilk oda denemesi.", null, null, null, null, null, ["Kamera, LiDAR ve fused snapshot ayrımı başladı.", "Harita kullanılabilir ama final kalitesinde değil."]),
            ["maps3"] = new("Maps3", "Tünel Denemesi", "Sınırlı", "bad", "4 dk", "Tünel geometrisinde kısa süreli SLAM testi.", 135, 323, 1209799, 442008, null, ["Tünel senaryosu için ilk sonuç alındı.", "Kısa süre ve rota nedeniyle eksik bölgeler kaldı."]),
            ["maps4"] = new("Maps4", "Geniş Tünel / Galeri", "Galeri", "warn", "8 dk", "Daha geniş ve uzun kayıtlı galeri ortamı.", 214, 599, 1894926, 595514, null, ["Pose sayısı yükseldi ve ortam daha büyük gezildi.", "Yan görünüm ve BEV sunum çıktıları oluştu."]),
            ["maps5"] = new("Maps5", "Yavaş Rota ve RTAB-Map Ayarı", "Güçlü", "ok", "9 dk", "Drone yavaşlatıldı, RTAB-Map ayarları ve rota iyileştirildi.", 156, 480, 1723383, 904960, null, ["Yavaş hareketin harita kalitesini artırdığı görüldü.", "Final sunum için güçlü karşılaştırma çıktısı."]),
            ["maps6"] = new("Maps6", "Çoklu Depth Kamera Füzyonu", "RGB-D", "ok", "9 dk", "Sağ ve sol depth kameralar eklendi.", 131, 402, 1459850, 841315, null, ["Front, left ve right RGB-D snapshotları üretildi.", "Kamera eklemek tek başına mesh kalitesini garanti etmedi."]),
            ["maps7"] = new("Maps7", "Coverage Rota İyileştirme", "Final", "ok", "9 dk", "Coverage rotası ve recovery iyileştirildi.", 157, 447, 1483804, 977665, null, ["Coverage rotası en dengeli sonuçlardan birini verdi.", "Harita final sunum için güçlü adaylardan biri."]),
            ["maps8"] = new("Maps8", "Waypoint'siz Otonom Keşif", "Otonom", "warn", "9 dk", "Visited-grid, lidar açıklığı ve recovery skorlarıyla otonom yön seçimi denendi.", 172, 561, 1686127, 906051, 55.1m, ["Waypoint listesi yok; hareket yönü anlık skor fonksiyonuyla seçildi.", "Tam profesyonel frontier planner değil; ama gerçek otonom coverage mantığını gösteriyor."]),
            ["maps9"] = new("Maps9", "Desenli Tünel Waypoint Keşfi", "Deneysel", "warn", "10 dk", "Sağa sola dönen desenli tünelde yavaş waypoint keşfi.", 110, 263, 1660820, 614013, null, ["Desenli ve dönüşlü tünel ortamında çıktı alındı.", "Bazı waypoint skip ve loop closure problemleri kaldı; Maps10 için ders niteliğinde."]),
            ["maps10"] = new("Maps10", "Genel Otonom Keşif / Yeni Harita", "Genel", "ok", "9 dk", "Haritaya özel waypoint yazmadan çalışan genel otonom keşif algoritmasıyla yeni ortamda kayıt alındı.", 166, 391, 1281401, 1032035, null, ["Haritaya özel rota yazılmadı; Maps10 genel otonom keşif algoritmasıyla çalıştı.", "RTAB-Map export sonucunda 1.03 milyon voxel noktalı cloud üretildi.", "CloudCompare mesh çıktısı web için GLB/OBJ bağlantılarıyla eklendi."]),
            ["maps11"] = new("Maps11", "Zorlu Dönüşlü Tünel", "Tünel", "ok", "9 dk", "Sağa sola dönen zorlu tünel ortamında aynı genel otonom keşif sistemiyle SLAM ve mesh çıktısı alındı.", 152, 443, 1133121, 599763, null, ["Maps10 ile aynı genel otonom algoritma kullanıldı; haritaya özel rota yazılmadı.", "Dönüşlü tünel ve dar geçişler sistemin daha zorlandığı senaryo olarak eklendi.", "CloudCompare mesh çıktısı webde önizleme ve dosya bağlantılarıyla sunuluyor."]),
            ["maps12"] = new("Maps12", "Genel SLAM Benchmark Haritası", "Benchmark", "ok", "9 dk", "Odalar, loop koridor, dar geçişler, kolonlar, kutular ve ağaç benzeri engeller içeren farklı benchmark haritasında aynı genel otonom algoritma test edildi.", 151, 373, 1498090, 845870, null, ["Maps10/11 ile aynı genel otonom algoritma kullanıldı; haritaya özel rota yazılmadı.", "Genel SLAM testlerine benzeyen loop oda/koridor düzeninde denendi.", "CloudCompare mesh çıktısı web için GLB/OBJ bağlantılarıyla eklendi."])
        };
    }
}
