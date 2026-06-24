using DroneSlam.Domain.Entities;
using Microsoft.EntityFrameworkCore;

namespace DroneSlam.Infrastructure.Persistence;

public sealed class DroneSlamDbContext(DbContextOptions<DroneSlamDbContext> options) : DbContext(options)
{
    public DbSet<MapRun> MapRuns => Set<MapRun>();
    public DbSet<MapAsset> MapAssets => Set<MapAsset>();
    public DbSet<MapMetric> MapMetrics => Set<MapMetric>();
    public DbSet<MapNote> MapNotes => Set<MapNote>();

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.Entity<MapRun>(entity =>
        {
            entity.HasKey(x => x.Id);
            entity.HasIndex(x => x.MapKey).IsUnique();
            entity.Property(x => x.MapKey).HasMaxLength(32).IsRequired();
            entity.Property(x => x.Name).HasMaxLength(80).IsRequired();
            entity.Property(x => x.Title).HasMaxLength(180).IsRequired();
            entity.Property(x => x.Label).HasMaxLength(40);
            entity.Property(x => x.Quality).HasMaxLength(20);
            entity.Property(x => x.Period).HasMaxLength(40);
            entity.Property(x => x.RelativeRunPath).HasMaxLength(600);
            entity.Property(x => x.AbsoluteRunPath).HasMaxLength(1000);

            entity.HasOne(x => x.Metric)
                .WithOne(x => x.MapRun)
                .HasForeignKey<MapMetric>(x => x.MapRunId)
                .OnDelete(DeleteBehavior.Cascade);
        });

        modelBuilder.Entity<MapAsset>(entity =>
        {
            entity.HasKey(x => x.Id);
            entity.HasIndex(x => new { x.MapRunId, x.AssetType }).IsUnique();
            entity.Property(x => x.AssetType).HasMaxLength(80).IsRequired();
            entity.Property(x => x.DisplayName).HasMaxLength(160).IsRequired();
            entity.Property(x => x.RelativePath).HasMaxLength(1000);
            entity.Property(x => x.AbsolutePath).HasMaxLength(1400);
            entity.Property(x => x.ContentType).HasMaxLength(120);
        });

        modelBuilder.Entity<MapMetric>(entity =>
        {
            entity.HasKey(x => x.Id);
            entity.Property(x => x.CoveragePercent).HasPrecision(6, 2);
        });

        modelBuilder.Entity<MapNote>(entity =>
        {
            entity.HasKey(x => x.Id);
            entity.Property(x => x.Text).HasMaxLength(600).IsRequired();
        });
    }
}
