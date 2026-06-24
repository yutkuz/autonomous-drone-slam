using DroneSlam.Application.Interfaces;
using DroneSlam.Domain.Entities;
using DroneSlam.Infrastructure.Persistence;
using Microsoft.EntityFrameworkCore;

namespace DroneSlam.Infrastructure.Repositories;

public sealed class MapRunRepository(DroneSlamDbContext dbContext) : IMapRunRepository
{
    public async Task<IReadOnlyList<MapRun>> GetAllAsync(CancellationToken cancellationToken)
    {
        return await dbContext.MapRuns
            .AsNoTracking()
            .Include(x => x.Metric)
            .Include(x => x.Assets)
            .Include(x => x.Notes)
            .OrderBy(x => x.MapKey.Length)
            .ThenBy(x => x.MapKey)
            .ToListAsync(cancellationToken);
    }

    public async Task<MapRun?> GetByIdAsync(Guid id, CancellationToken cancellationToken)
    {
        return await dbContext.MapRuns
            .AsNoTracking()
            .Include(x => x.Metric)
            .Include(x => x.Assets)
            .Include(x => x.Notes)
            .FirstOrDefaultAsync(x => x.Id == id, cancellationToken);
    }

    public async Task<MapRun?> GetByMapKeyAsync(string mapKey, CancellationToken cancellationToken)
    {
        return await dbContext.MapRuns
            .AsNoTracking()
            .Include(x => x.Metric)
            .Include(x => x.Assets)
            .Include(x => x.Notes)
            .FirstOrDefaultAsync(x => x.MapKey == mapKey, cancellationToken);
    }

    public async Task<MapAsset?> GetAssetAsync(Guid mapRunId, string assetType, CancellationToken cancellationToken)
    {
        return await dbContext.MapAssets
            .AsNoTracking()
            .FirstOrDefaultAsync(x => x.MapRunId == mapRunId && x.AssetType == assetType, cancellationToken);
    }

    public async Task UpsertRangeAsync(IReadOnlyList<MapRun> mapRuns, CancellationToken cancellationToken)
    {
        foreach (var incoming in mapRuns)
        {
            var existing = await dbContext.MapRuns
                .Include(x => x.Metric)
                .Include(x => x.Assets)
                .Include(x => x.Notes)
                .FirstOrDefaultAsync(x => x.MapKey == incoming.MapKey, cancellationToken);

            if (existing is null)
            {
                dbContext.MapRuns.Add(incoming);
                continue;
            }

            dbContext.MapRuns.Remove(existing);
            await dbContext.SaveChangesAsync(cancellationToken);
            dbContext.MapRuns.Add(incoming);
        }

        await dbContext.SaveChangesAsync(cancellationToken);
    }
}
