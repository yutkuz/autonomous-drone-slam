using DroneSlam.Application.Interfaces;
using DroneSlam.Application.Options;
using DroneSlam.Infrastructure.Persistence;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Options;

namespace DroneSlam.Api.HostedServices;

public sealed class DatabaseStartupService(
    IServiceProvider serviceProvider,
    IOptions<ProjectFinalOptions> options,
    ILogger<DatabaseStartupService> logger) : IHostedService
{
    public async Task StartAsync(CancellationToken cancellationToken)
    {
        if (!options.Value.AutoMigrateOnStartup && !options.Value.AutoImportOnStartup) return;

        using var scope = serviceProvider.CreateScope();

        if (options.Value.AutoMigrateOnStartup)
        {
            logger.LogInformation("Applying DroneSlamDb migrations.");
            var dbContext = scope.ServiceProvider.GetRequiredService<DroneSlamDbContext>();
            await dbContext.Database.MigrateAsync(cancellationToken);
        }

        if (options.Value.AutoImportOnStartup)
        {
            logger.LogInformation("Importing Project-Final map outputs.");
            var importer = scope.ServiceProvider.GetRequiredService<IMapImportService>();
            await importer.ImportProjectFinalAsync(cancellationToken);
        }
    }

    public Task StopAsync(CancellationToken cancellationToken) => Task.CompletedTask;
}
