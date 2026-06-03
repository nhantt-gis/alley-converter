"""Core CSV to GeoPackage conversion workflow."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import geopandas as gpd
import pandas as pd

from alley_converter.config import ConverterConfig
from alley_converter.exceptions import (
    LayerNameConflictError,
    MissingGeometryColumnError,
    NoInputFilesError,
    NoValidCsvError,
)
from alley_converter.geometry import parse_geojson_geometry


@dataclass(frozen=True)
class LayerConversion:
    """Metadata for one converted CSV layer."""

    source_path: Path
    layer_name: str
    feature_count: int
    invalid_geometry_count: int = 0


@dataclass(frozen=True)
class ConversionResult:
    """Summary returned after a directory conversion job."""

    output_path: Path
    combined_layer: str
    combined_feature_count: int
    layers: list[LayerConversion] = field(default_factory=list)
    skipped_files: dict[str, str] = field(default_factory=dict)

    @property
    def layer_counts(self) -> dict[str, int]:
        """Return a layer-name to feature-count mapping."""

        counts = {layer.layer_name: layer.feature_count for layer in self.layers}
        counts[self.combined_layer] = self.combined_feature_count
        return counts


def discover_csv_files(input_dir: Path) -> list[Path]:
    """Return CSV files in deterministic order."""

    return sorted(input_dir.glob("*.csv"))


def csv_to_geodataframe(
    csv_path: Path,
    *,
    geometry_column: str,
    crs: str,
    drop_invalid_geometry: bool,
) -> tuple[gpd.GeoDataFrame, int]:
    """Read a CSV file and convert the configured GeoJSON column to geometry."""

    df = pd.read_csv(csv_path, dtype={geometry_column: str})

    if geometry_column not in df.columns:
        raise MissingGeometryColumnError(
            f"{csv_path.name}: missing required column '{geometry_column}'."
        )

    geometries = df[geometry_column].map(parse_geojson_geometry)
    invalid_geometry_count = int(geometries.isna().sum())
    df[geometry_column] = geometries

    gdf = gpd.GeoDataFrame(df, geometry=geometry_column, crs=crs)

    if drop_invalid_geometry and invalid_geometry_count:
        gdf = gdf[gdf.geometry.notna()].copy()

    return gdf, invalid_geometry_count


def convert_directory(config: ConverterConfig) -> ConversionResult:
    """Convert every ``*.csv`` in ``config.input_dir`` to one GeoPackage."""

    if not config.input_dir.is_dir():
        raise FileNotFoundError(f"Input directory not found: {config.input_dir}")

    csv_files = discover_csv_files(config.input_dir)
    if not csv_files:
        raise NoInputFilesError(f"No CSV files found in '{config.input_dir}'.")

    if config.combined_layer in {csv_path.stem for csv_path in csv_files}:
        raise LayerNameConflictError(
            f"Combined layer '{config.combined_layer}' conflicts with an input CSV name."
        )

    config.output_path.parent.mkdir(parents=True, exist_ok=True)
    if config.overwrite and config.output_path.exists():
        config.output_path.unlink()

    geodataframes: list[gpd.GeoDataFrame] = []
    converted_layers: list[LayerConversion] = []
    skipped_files: dict[str, str] = {}

    for csv_path in csv_files:
        layer_name = csv_path.stem

        try:
            gdf, invalid_geometry_count = csv_to_geodataframe(
                csv_path,
                geometry_column=config.geometry_column,
                crs=config.output_crs,
                drop_invalid_geometry=config.drop_invalid_geometry,
            )
        except MissingGeometryColumnError as exc:
            skipped_files[csv_path.name] = str(exc)
            continue

        if gdf.empty:
            skipped_files[csv_path.name] = "No rows available after geometry filtering."
            continue

        gdf.to_file(config.output_path, driver="GPKG", layer=layer_name)
        geodataframes.append(gdf)
        converted_layers.append(
            LayerConversion(
                source_path=csv_path,
                layer_name=layer_name,
                feature_count=len(gdf),
                invalid_geometry_count=invalid_geometry_count,
            )
        )

    if not geodataframes:
        raise NoValidCsvError("No valid CSV files were converted.")

    combined = gpd.GeoDataFrame(
        pd.concat(geodataframes, ignore_index=True),
        geometry=config.geometry_column,
        crs=config.output_crs,
    )
    combined.to_file(config.output_path, driver="GPKG", layer=config.combined_layer)

    return ConversionResult(
        output_path=config.output_path,
        combined_layer=config.combined_layer,
        combined_feature_count=len(combined),
        layers=converted_layers,
        skipped_files=skipped_files,
    )
