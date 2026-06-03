"""Shared defaults for the converter."""

from dataclasses import dataclass
from pathlib import Path

DEFAULT_DATA_DIR = Path("data")
DEFAULT_INPUT_DIR = DEFAULT_DATA_DIR
DEFAULT_OUTPUT_PATH = DEFAULT_DATA_DIR / "data.gpkg"
DEFAULT_GEOMETRY_COLUMN = "geometry"
DEFAULT_OUTPUT_CRS = "EPSG:4326"
DEFAULT_COMBINED_LAYER = "combined"


@dataclass(frozen=True)
class ConverterConfig:
    """Runtime configuration for a directory conversion job."""

    input_dir: Path = DEFAULT_INPUT_DIR
    output_path: Path = DEFAULT_OUTPUT_PATH
    geometry_column: str = DEFAULT_GEOMETRY_COLUMN
    output_crs: str = DEFAULT_OUTPUT_CRS
    combined_layer: str = DEFAULT_COMBINED_LAYER
    overwrite: bool = True
    drop_invalid_geometry: bool = False
