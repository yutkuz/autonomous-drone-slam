namespace DroneSlam.Application.DTOs;

public sealed record MapRunDto(
    Guid Id,
    string MapKey,
    string Name,
    string Title,
    string Label,
    string Quality,
    string Period,
    string Summary,
    string RelativeRunPath,
    DateTimeOffset? FlightStartedAt,
    DateTimeOffset ImportedAt,
    MapMetricDto Stats,
    IReadOnlyDictionary<string, string> Assets,
    IReadOnlyList<MapAssetDto> Files,
    IReadOnlyList<string> Notes);
