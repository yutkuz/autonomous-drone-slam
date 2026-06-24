using DroneSlam.Application.DTOs;

namespace DroneSlam.Application.Interfaces;

public interface IMapImportService
{
    Task<ImportResultDto> ImportProjectFinalAsync(CancellationToken cancellationToken);
}
