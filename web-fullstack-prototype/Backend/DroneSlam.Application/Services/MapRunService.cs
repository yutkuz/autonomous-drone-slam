using DroneSlam.Application.DTOs;
using DroneSlam.Application.Interfaces;
using DroneSlam.Domain.Entities;

namespace DroneSlam.Application.Services;

public sealed class MapRunService(IMapRunRepository repository) : IMapRunService
{
    public async Task<IReadOnlyList<MapRunDto>> GetAllAsync(CancellationToken cancellationToken)
    {
        var maps = await repository.GetAllAsync(cancellationToken);
        return maps.Select(ToDto).ToList();
    }

    public async Task<MapRunDto?> GetByIdAsync(Guid id, CancellationToken cancellationToken)
    {
        var map = await repository.GetByIdAsync(id, cancellationToken);
        return map is null ? null : ToDto(map);
    }

    public async Task<MapAssetDto?> GetAssetAsync(Guid mapRunId, string assetType, CancellationToken cancellationToken)
    {
        var asset = await repository.GetAssetAsync(mapRunId, assetType, cancellationToken);
        return asset is null ? null : ToAssetDto(asset, mapRunId);
    }

    private static MapRunDto ToDto(MapRun map)
    {
        var assets = map.Assets
            .Where(asset => asset.ExistsOnDisk)
            .ToDictionary(
                asset => asset.AssetType,
                asset => $"/api/maps/{map.Id}/assets/{asset.AssetType}/file",
                StringComparer.OrdinalIgnoreCase);

        var files = map.Assets
            .OrderBy(asset => asset.AssetType)
            .Select(asset => ToAssetDto(asset, map.Id))
            .ToList();

        return new MapRunDto(
            map.Id,
            map.MapKey,
            map.Name,
            map.Title,
            map.Label,
            map.Quality,
            map.Period,
            map.Summary,
            map.RelativeRunPath,
            map.FlightStartedAt,
            map.ImportedAt,
            ToMetricDto(map.Metric),
            assets,
            files,
            map.Notes.OrderBy(note => note.SortOrder).Select(note => note.Text).ToList());
    }

    private static MapAssetDto ToAssetDto(MapAsset asset, Guid mapRunId)
    {
        var url = asset.ExistsOnDisk ? $"/api/maps/{mapRunId}/assets/{asset.AssetType}/file" : null;
        return new MapAssetDto(asset.AssetType, asset.DisplayName, url, asset.RelativePath, asset.SizeBytes, asset.ExistsOnDisk);
    }

    private static MapMetricDto ToMetricDto(MapMetric? metric)
    {
        return new MapMetricDto(
            metric?.PoseCount,
            metric?.LinkCount,
            metric?.RawPointCount,
            metric?.VoxelPointCount,
            metric?.CoveragePercent,
            FormatBytes(metric?.DatabaseSizeBytes),
            FormatBytes(metric?.PointCloudSizeBytes),
            FormatBytes(metric?.MeshSizeBytes));
    }

    private static string FormatBytes(long? bytes)
    {
        if (bytes is null or <= 0) return "-";
        string[] units = ["B", "KB", "MB", "GB"];
        var size = (double)bytes.Value;
        var unit = 0;
        while (size >= 1024 && unit < units.Length - 1)
        {
            size /= 1024;
            unit++;
        }

        return $"{size:0.#} {units[unit]}";
    }
}
