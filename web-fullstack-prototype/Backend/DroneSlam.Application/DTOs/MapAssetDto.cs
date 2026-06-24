namespace DroneSlam.Application.DTOs;

public sealed record MapAssetDto(
    string AssetType,
    string DisplayName,
    string? Url,
    string RelativePath,
    long SizeBytes,
    bool ExistsOnDisk);
