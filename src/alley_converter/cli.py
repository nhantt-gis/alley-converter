"""Typer/Rich command line interface."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from alley_converter import __version__
from alley_converter.config import (
    DEFAULT_COMBINED_LAYER,
    DEFAULT_GEOMETRY_COLUMN,
    DEFAULT_INPUT_DIR,
    DEFAULT_OUTPUT_CRS,
    DEFAULT_OUTPUT_PATH,
    ConverterConfig,
)
from alley_converter.converter import ConversionResult, convert_directory
from alley_converter.exceptions import AlleyConverterError

app = typer.Typer(
    add_completion=False,
    context_settings={"help_option_names": ["-h", "--help"]},
    help="Convert CSV files with GeoJSON geometry columns into a GeoPackage.",
)
console = Console()


def _render_result(result: ConversionResult) -> None:
    table = Table(title="Converted layers", show_lines=False)
    table.add_column("Layer", style="cyan", no_wrap=True)
    table.add_column("Source CSV", style="white")
    table.add_column("Features", justify="right", style="green")
    table.add_column("Invalid geometry", justify="right", style="yellow")

    for layer in result.layers:
        table.add_row(
            layer.layer_name,
            layer.source_path.name,
            str(layer.feature_count),
            str(layer.invalid_geometry_count),
        )

    table.add_section()
    table.add_row(
        result.combined_layer,
        "combined",
        str(result.combined_feature_count),
        "-",
    )

    console.print(table)

    if result.skipped_files:
        skipped = Table(title="Skipped files")
        skipped.add_column("CSV", style="yellow")
        skipped.add_column("Reason", style="white")
        for name, reason in result.skipped_files.items():
            skipped.add_row(name, reason)
        console.print(skipped)

    console.print(
        Panel.fit(
            f"[bold green]Success[/bold green]\nGeoPackage: [cyan]{result.output_path}[/cyan]",
            border_style="green",
        )
    )


@app.command()
def convert(
    input_dir: Annotated[
        Path,
        typer.Option(
            "--input",
            "-i",
            file_okay=False,
            dir_okay=True,
            readable=True,
            help="Directory containing input CSV files.",
        ),
    ] = DEFAULT_INPUT_DIR,
    output_path: Annotated[
        Path,
        typer.Option(
            "--output",
            "-o",
            dir_okay=False,
            help="Output GeoPackage path.",
        ),
    ] = DEFAULT_OUTPUT_PATH,
    combined_layer: Annotated[
        str,
        typer.Option(
            "--combined-layer",
            help="Name of the merged layer containing all converted features.",
        ),
    ] = DEFAULT_COMBINED_LAYER,
    geometry_column: Annotated[
        str,
        typer.Option(
            "--geometry-column",
            help="CSV column containing GeoJSON geometry strings.",
        ),
    ] = DEFAULT_GEOMETRY_COLUMN,
    output_crs: Annotated[
        str,
        typer.Option("--crs", help="CRS assigned to output layers."),
    ] = DEFAULT_OUTPUT_CRS,
    overwrite: Annotated[
        bool,
        typer.Option(
            "--overwrite/--no-overwrite",
            help="Replace an existing output file before writing.",
        ),
    ] = True,
    drop_invalid_geometry: Annotated[
        bool,
        typer.Option(
            "--drop-invalid-geometry/--keep-invalid-geometry",
            help="Drop rows whose geometry column cannot be parsed.",
        ),
    ] = False,
    version: Annotated[
        bool,
        typer.Option("--version", help="Show the application version and exit."),
    ] = False,
) -> None:
    """Convert every CSV file in a directory into a layer inside one GPKG."""

    if version:
        console.print(f"alley-converter {__version__}")
        raise typer.Exit()

    config = ConverterConfig(
        input_dir=input_dir,
        output_path=output_path,
        combined_layer=combined_layer,
        geometry_column=geometry_column,
        output_crs=output_crs,
        overwrite=overwrite,
        drop_invalid_geometry=drop_invalid_geometry,
    )

    console.print(
        Panel.fit(
            "\n".join(
                [
                    "[bold]GTEL Maps Alley Geodata Convert Tool[/bold]",
                    f"Input : [cyan]{config.input_dir}[/cyan]",
                    f"Output: [cyan]{config.output_path}[/cyan]",
                    f"CRS   : [cyan]{config.output_crs}[/cyan]",
                ]
            ),
            border_style="cyan",
        )
    )

    try:
        with console.status("[bold cyan]Converting CSV files...[/bold cyan]"):
            result = convert_directory(config)
    except (AlleyConverterError, FileNotFoundError, OSError) as exc:
        console.print(f"[bold red]Error:[/bold red] {exc}")
        raise typer.Exit(code=1) from exc

    _render_result(result)
