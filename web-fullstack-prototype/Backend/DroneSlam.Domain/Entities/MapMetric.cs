namespace DroneSlam.Domain.Entities;

public sealed class MapMetric
{
    public Guid Id { get; set; }
    public Guid MapRunId { get; set; }
    public int? PoseCount { get; set; }
    public int? LinkCount { get; set; }
    public long? RawPointCount { get; set; }
    public long? VoxelPointCount { get; set; }
    public decimal? CoveragePercent { get; set; }
    public long? DatabaseSizeBytes { get; set; }
    public long? PointCloudSizeBytes { get; set; }
    public long? MeshSizeBytes { get; set; }

    public MapRun? MapRun { get; set; }
}
