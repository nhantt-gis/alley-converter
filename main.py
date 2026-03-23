"""Convert alley Excel data to GeoPackage (GPKG)."""

import argparse
import json
import sys
from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely.geometry import shape

INPUT_GEOMETRY_COLUMN = "geometry"
OUTPUT_CRS = "EPSG:4326"


def parse_geometry(geojson_str: str):
    """Parse a GeoJSON/Feature string into a Shapely geometry."""
    if not isinstance(geojson_str, str) or not geojson_str.strip():
        return None

    try:
        data = json.loads(geojson_str)
        return shape(data)
    except Exception:
        return None


def convert(input_path: Path, output_path: Path, layer: str) -> int:
    """Read Excel, convert geometry column, and write a GPKG file."""
    df = pd.read_excel(input_path, dtype={INPUT_GEOMETRY_COLUMN: str})

    if INPUT_GEOMETRY_COLUMN not in df.columns:
        raise ValueError(
            f"Missing required column '{INPUT_GEOMETRY_COLUMN}' in input file."
        )

    df[INPUT_GEOMETRY_COLUMN] = df[INPUT_GEOMETRY_COLUMN].apply(parse_geometry)
    gdf = gpd.GeoDataFrame(df, geometry=INPUT_GEOMETRY_COLUMN, crs=OUTPUT_CRS)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    gdf.to_file(output_path, driver="GPKG", layer=layer)
    return len(gdf)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Convert Excel to GeoPackage (GPKG).",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-i",
        "--input",
        type=Path,
        default=Path("input/data.xlsx"),
        metavar="FILE",
        help="Input Excel file path",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("output/data.gpkg"),
        metavar="FILE",
        help="Output GPKG file path",
    )
    parser.add_argument(
        "-l",
        "--layer",
        default="data",
        metavar="NAME",
        help="Layer name inside the GPKG",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()

    if not args.input.exists():
        print(f"Input file not found: {args.input}")
        sys.exit(1)

    try:
        count = convert(args.input, args.output, args.layer)
    except ValueError as exc:
        print(exc)
        sys.exit(1)

    if count == 0:
        print("No rows were written to output.")
        sys.exit(1)

    print(f"Successfully converted {count} rows to {args.output} (layer: {args.layer}).")


if __name__ == "__main__":
    main()
