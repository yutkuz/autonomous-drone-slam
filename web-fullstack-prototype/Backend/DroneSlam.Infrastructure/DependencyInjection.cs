using DroneSlam.Application.Interfaces;
using DroneSlam.Application.Options;
using DroneSlam.Infrastructure.Persistence;
using DroneSlam.Infrastructure.Repositories;
using DroneSlam.Infrastructure.Services;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;

namespace DroneSlam.Infrastructure;

public static class DependencyInjection
{
    public static IServiceCollection AddInfrastructure(this IServiceCollection services, IConfiguration configuration)
    {
        services.Configure<ProjectFinalOptions>(options =>
        {
            var section = configuration.GetSection("ProjectFinal");
            options.RootPath = section["RootPath"] ?? options.RootPath;
            options.AutoImportOnStartup = bool.TryParse(section["AutoImportOnStartup"], out var autoImport) && autoImport;
            options.AutoMigrateOnStartup = bool.TryParse(section["AutoMigrateOnStartup"], out var autoMigrate) && autoMigrate;
        });

        services.AddDbContext<DroneSlamDbContext>(options =>
        {
            var connectionString = configuration.GetConnectionString("DroneSlamDb");
            options.UseSqlServer(connectionString);
        });

        services.AddScoped<IMapRunRepository, MapRunRepository>();
        services.AddScoped<IMapImportService, ProjectFinalImportService>();
        return services;
    }
}
