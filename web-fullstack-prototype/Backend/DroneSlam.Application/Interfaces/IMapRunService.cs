using DroneSlam.Application.DTOs;

namespace DroneSlam.Application.Interfaces;

public interface IMapRunService
{
    Task<IReadOnlyList<MapRunDto>> GetAllAsync(CancellationToken cancellationToken);
    Task<MapRunDto?> GetByIdAsync(Guid id, CancellationToken cancellationToken);
    Task<MapAssetDto?> GetAssetAsync(Guid mapRunId, string assetType, CancellationToken cancellationToken);
}
