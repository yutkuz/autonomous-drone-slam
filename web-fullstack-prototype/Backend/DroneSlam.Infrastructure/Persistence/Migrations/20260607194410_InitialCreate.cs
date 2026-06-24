using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace DroneSlam.Infrastructure.Persistence.Migrations
{
    /// <inheritdoc />
    public partial class InitialCreate : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.CreateTable(
                name: "MapRuns",
                columns: table => new
                {
                    Id = table.Column<Guid>(type: "uniqueidentifier", nullable: false),
                    MapKey = table.Column<string>(type: "nvarchar(32)", maxLength: 32, nullable: false),
                    Name = table.Column<string>(type: "nvarchar(80)", maxLength: 80, nullable: false),
                    Title = table.Column<string>(type: "nvarchar(180)", maxLength: 180, nullable: false),
                    Label = table.Column<string>(type: "nvarchar(40)", maxLength: 40, nullable: false),
                    Quality = table.Column<string>(type: "nvarchar(20)", maxLength: 20, nullable: false),
                    Period = table.Column<string>(type: "nvarchar(40)", maxLength: 40, nullable: false),
                    Summary = table.Column<string>(type: "nvarchar(max)", nullable: false),
                    RelativeRunPath = table.Column<string>(type: "nvarchar(600)", maxLength: 600, nullable: false),
                    AbsoluteRunPath = table.Column<string>(type: "nvarchar(1000)", maxLength: 1000, nullable: false),
                    FlightStartedAt = table.Column<DateTimeOffset>(type: "datetimeoffset", nullable: true),
                    ImportedAt = table.Column<DateTimeOffset>(type: "datetimeoffset", nullable: false),
                    IsAvailable = table.Column<bool>(type: "bit", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_MapRuns", x => x.Id);
                });

            migrationBuilder.CreateTable(
                name: "MapAssets",
                columns: table => new
                {
                    Id = table.Column<Guid>(type: "uniqueidentifier", nullable: false),
                    MapRunId = table.Column<Guid>(type: "uniqueidentifier", nullable: false),
                    AssetType = table.Column<string>(type: "nvarchar(80)", maxLength: 80, nullable: false),
                    DisplayName = table.Column<string>(type: "nvarchar(160)", maxLength: 160, nullable: false),
                    RelativePath = table.Column<string>(type: "nvarchar(1000)", maxLength: 1000, nullable: false),
                    AbsolutePath = table.Column<string>(type: "nvarchar(1400)", maxLength: 1400, nullable: false),
                    ContentType = table.Column<string>(type: "nvarchar(120)", maxLength: 120, nullable: false),
                    SizeBytes = table.Column<long>(type: "bigint", nullable: false),
                    ExistsOnDisk = table.Column<bool>(type: "bit", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_MapAssets", x => x.Id);
                    table.ForeignKey(
                        name: "FK_MapAssets_MapRuns_MapRunId",
                        column: x => x.MapRunId,
                        principalTable: "MapRuns",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateTable(
                name: "MapMetrics",
                columns: table => new
                {
                    Id = table.Column<Guid>(type: "uniqueidentifier", nullable: false),
                    MapRunId = table.Column<Guid>(type: "uniqueidentifier", nullable: false),
                    PoseCount = table.Column<int>(type: "int", nullable: true),
                    LinkCount = table.Column<int>(type: "int", nullable: true),
                    RawPointCount = table.Column<long>(type: "bigint", nullable: true),
                    VoxelPointCount = table.Column<long>(type: "bigint", nullable: true),
                    CoveragePercent = table.Column<decimal>(type: "decimal(6,2)", precision: 6, scale: 2, nullable: true),
                    DatabaseSizeBytes = table.Column<long>(type: "bigint", nullable: true),
                    PointCloudSizeBytes = table.Column<long>(type: "bigint", nullable: true),
                    MeshSizeBytes = table.Column<long>(type: "bigint", nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_MapMetrics", x => x.Id);
                    table.ForeignKey(
                        name: "FK_MapMetrics_MapRuns_MapRunId",
                        column: x => x.MapRunId,
                        principalTable: "MapRuns",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateTable(
                name: "MapNotes",
                columns: table => new
                {
                    Id = table.Column<Guid>(type: "uniqueidentifier", nullable: false),
                    MapRunId = table.Column<Guid>(type: "uniqueidentifier", nullable: false),
                    SortOrder = table.Column<int>(type: "int", nullable: false),
                    Text = table.Column<string>(type: "nvarchar(600)", maxLength: 600, nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_MapNotes", x => x.Id);
                    table.ForeignKey(
                        name: "FK_MapNotes_MapRuns_MapRunId",
                        column: x => x.MapRunId,
                        principalTable: "MapRuns",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateIndex(
                name: "IX_MapAssets_MapRunId_AssetType",
                table: "MapAssets",
                columns: new[] { "MapRunId", "AssetType" },
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_MapMetrics_MapRunId",
                table: "MapMetrics",
                column: "MapRunId",
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_MapNotes_MapRunId",
                table: "MapNotes",
                column: "MapRunId");

            migrationBuilder.CreateIndex(
                name: "IX_MapRuns_MapKey",
                table: "MapRuns",
                column: "MapKey",
                unique: true);
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropTable(
                name: "MapAssets");

            migrationBuilder.DropTable(
                name: "MapMetrics");

            migrationBuilder.DropTable(
                name: "MapNotes");

            migrationBuilder.DropTable(
                name: "MapRuns");
        }
    }
}
