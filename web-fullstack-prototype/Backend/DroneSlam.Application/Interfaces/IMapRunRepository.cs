using DroneSlam.Domain.Entities;

namespace DroneSlam.Application.Interfaces;

public interface IMapRunRepository
{
    Task<IReadOnlyList<MapRun>> GetAllAsync(CancellationToken cancellationToken);
    Task<MapRun?> GetByIdAsync(Guid id, CancellationToken cancellationToken);
    Task<MapRun?> GetByMapKeyAsync(string mapKey, CancellationToken cancellationToken);
    Task<MapAsset?> GetAssetAsync(Guid mapRunId, string assetType, CancellationToken cancellationToken);
    Task UpsertRangeAsync(IReadOnlyList<MapRun> mapRuns, CancellationToken cancellationToken);
}
