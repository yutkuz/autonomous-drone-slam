namespace DroneSlam.Domain.Entities;

public sealed class MapNote
{
    public Guid Id { get; set; }
    public Guid MapRunId { get; set; }
    public int SortOrder { get; set; }
    public string Text { get; set; } = string.Empty;

    public MapRun? MapRun { get; set; }
}
