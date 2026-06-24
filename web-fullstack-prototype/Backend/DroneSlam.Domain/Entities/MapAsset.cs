namespace DroneSlam.Domain.Entities;

public sealed class MapAsset
{
    public Guid Id { get; set; }
    public Guid MapRunId { get; set; }
    public string AssetType { get; set; } = string.Empty;
    public string DisplayName { get; set; } = string.Empty;
    public string RelativePath { get; set; } = string.Empty;
    public string AbsolutePath { get; set; } = string.Empty;
    public string ContentType { get; set; } = "application/octet-stream";
    public long SizeBytes { get; set; }
    public bool ExistsOnDisk { get; set; }

    public MapRun? MapRun { get; set; }
}
