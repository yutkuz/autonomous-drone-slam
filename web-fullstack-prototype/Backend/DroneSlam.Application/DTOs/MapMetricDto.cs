namespace DroneSlam.Application.DTOs;

public sealed record MapMetricDto(
    int? Poses,
    int? Links,
    long? Raw,
    long? Voxel,
    decimal? Coverage,
    string DatabaseSize,
    string PointCloudSize,
    string MeshSize);
