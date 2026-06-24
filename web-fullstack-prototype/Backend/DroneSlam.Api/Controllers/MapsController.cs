using DroneSlam.Application.Interfaces;
using DroneSlam.Application.Options;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Options;

namespace DroneSlam.Api.Controllers;

[ApiController]
[Route("api/maps")]
public sealed class MapsController(
    IMapRunService mapRunService,
    IMapImportService importService,
    IOptions<ProjectFinalOptions> options) : ControllerBase
{
    [HttpGet]
    public async Task<IActionResult> GetAll(CancellationToken cancellationToken)
    {
        var maps = await mapRunService.GetAllAsync(cancellationToken);
        return Ok(maps);
    }

    [HttpGet("{id:guid}")]
    public async Task<IActionResult> GetById(Guid id, CancellationToken cancellationToken)
    {
        var map = await mapRunService.GetByIdAsync(id, cancellationToken);
        return map is null ? NotFound() : Ok(map);
    }

    [HttpPost("import")]
    public async Task<IActionResult> Import(CancellationToken cancellationToken)
    {
        var result = await importService.ImportProjectFinalAsync(cancellationToken);
        return Ok(result);
    }

    [HttpGet("{id:guid}/assets/{assetType}/file")]
    public async Task<IActionResult> GetAssetFile(Guid id, string assetType, CancellationToken cancellationToken)
    {
        var map = await mapRunService.GetByIdAsync(id, cancellationToken);
        var file = map?.Files.FirstOrDefault(x => x.AssetType.Equals(assetType, StringComparison.OrdinalIgnoreCase));
        if (file is null || !file.ExistsOnDisk) return NotFound();

        var root = Path.GetFullPath(options.Value.RootPath);
        var absolutePath = Path.GetFullPath(Path.Combine(root, file.RelativePath));
        if (!absolutePath.StartsWith(root, StringComparison.Ordinal)) return BadRequest("Invalid asset path.");
        if (!System.IO.File.Exists(absolutePath)) return NotFound();

        return PhysicalFile(absolutePath, GetContentType(absolutePath), Path.GetFileName(absolutePath), enableRangeProcessing: true);
    }

    private static string GetContentType(string path)
    {
        return Path.GetExtension(path).ToLowerInvariant() switch
        {
            ".png" => "image/png",
            ".jpg" or ".jpeg" => "image/jpeg",
            ".ply" => "application/octet-stream",
            ".db" => "application/octet-stream",
            ".obj" => "text/plain",
            ".txt" => "text/plain",
            _ => "application/octet-stream"
        };
    }
}
