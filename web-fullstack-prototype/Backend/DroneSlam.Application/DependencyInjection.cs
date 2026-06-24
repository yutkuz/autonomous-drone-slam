using DroneSlam.Application.Interfaces;
using DroneSlam.Application.Services;
using Microsoft.Extensions.DependencyInjection;

namespace DroneSlam.Application;

public static class DependencyInjection
{
    public static IServiceCollection AddApplication(this IServiceCollection services)
    {
        services.AddScoped<IMapRunService, MapRunService>();
        return services;
    }
}
