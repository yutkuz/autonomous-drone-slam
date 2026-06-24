namespace DroneSlam.Domain.Entities;

public sealed class MapRun
{
    public Guid Id { get; set; }
    public string MapKey { get; set; } = string.Empty;
    public string Name { get; set; } = string.Empty;
    public string Title { get; set; } = string.Empty;
    public string Label { get; set; } = string.Empty;
    public string Quality { get; set; } = "warn";
    public string Period { get; set; } = string.Empty;
    public string Summary { get; set; } = string.Empty;
    public string RelativeRunPath { get; set; } = string.Empty;
    public string AbsoluteRunPath { get; set; } = string.Empty;
    public DateTimeOffset? FlightStartedAt { get; set; }
    public DateTimeOffset ImportedAt { get; set; } = DateTimeOffset.UtcNow;
    public bool IsAvailable { get; set; } = true;

    public MapMetric? Metric { get; set; }
    public ICollection<MapAsset> Assets { get; set; } = new List<MapAsset>();
    public ICollection<MapNote> Notes { get; set; } = new List<MapNote>();
}
