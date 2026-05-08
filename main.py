"""Convert all CSV files in a directory to layers inside a single GeoPackage."""

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
    """Parse a GeoJSON string (geometry or Feature) into a Shapely geometry."""
    if not isinstance(geojson_str, str) or not geojson_str.strip():
        return None

    try:
        data = json.loads(geojson_str)
        if isinstance(data, dict) and data.get("type") == "Feature":
            return shape(data["geometry"])
        return shape(data)
    except Exception:
        return None


def csv_to_gdf(csv_path: Path) -> gpd.GeoDataFrame:
    """Read a CSV and return a GeoDataFrame. Raises ValueError on bad schema."""
    df = pd.read_csv(csv_path, dtype={INPUT_GEOMETRY_COLUMN: str})

    if INPUT_GEOMETRY_COLUMN not in df.columns:
        raise ValueError(
            f"{csv_path.name}: missing required column '{INPUT_GEOMETRY_COLUMN}'."
        )

    df[INPUT_GEOMETRY_COLUMN] = df[INPUT_GEOMETRY_COLUMN].apply(parse_geometry)
    return gpd.GeoDataFrame(df, geometry=INPUT_GEOMETRY_COLUMN, crs=OUTPUT_CRS)


def convert_directory(
    input_dir: Path,
    output_path: Path,
    combined_layer: str,
) -> dict[str, int]:
    """
    Convert every *.csv in *input_dir* to a layer in *output_path*.

    Each file becomes a layer named after its stem.  A merged layer named
    *combined_layer* is appended at the end.

    Returns a mapping of layer_name -> feature_count.
    """
    csv_files = sorted(input_dir.glob("*.csv"))
    if not csv_files:
        raise FileNotFoundError(f"No CSV files found in '{input_dir}'.")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    gdfs: list[gpd.GeoDataFrame] = []
    counts: dict[str, int] = {}

    for csv_path in csv_files:
        layer_name = csv_path.stem
        try:
            gdf = csv_to_gdf(csv_path)
        except ValueError as exc:
            print(f"  [SKIP] {exc}")
            continue

        gdf.to_file(output_path, driver="GPKG", layer=layer_name)
        gdfs.append(gdf)
        counts[layer_name] = len(gdf)
        print(f"  [OK]   {csv_path.name} -> layer '{layer_name}' ({len(gdf)} rows)")

    if not gdfs:
        raise ValueError("No valid CSV files were converted.")

    combined = gpd.GeoDataFrame(
        pd.concat(gdfs, ignore_index=True),
        geometry=INPUT_GEOMETRY_COLUMN,
        crs=OUTPUT_CRS,
    )
    combined.to_file(output_path, driver="GPKG", layer=combined_layer)
    counts[combined_layer] = len(combined)
    print(f"  [OK]   Combined layer '{combined_layer}' ({len(combined)} rows total)")

    return counts


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Convert all CSV files in a folder to layers in a GeoPackage.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-i",
        "--input",
        type=Path,
        default=Path("input"),
        metavar="DIR",
        help="Directory containing input CSV files",
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
        "--combined-layer",
        default="combined",
        metavar="NAME",
        help="Name of the merged layer that contains all features",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()

    if not args.input.is_dir():
        print(f"Input directory not found: {args.input}")
        sys.exit(1)

    print(f"Input dir : {args.input}")
    print(f"Output    : {args.output}")

    try:
        counts = convert_directory(args.input, args.output, args.combined_layer)
    except (FileNotFoundError, ValueError) as exc:
        print(f"Error: {exc}")
        sys.exit(1)

    print(f"\nThành công! File GeoPackage đã được tạo: {args.output}")
    print(f"Layers: {', '.join(counts.keys())}")


if __name__ == "__main__":
    main()
