namespace DroneSlam.Application.DTOs;

public sealed record ImportResultDto(int ImportedCount, int AssetCount, DateTimeOffset ImportedAt);
