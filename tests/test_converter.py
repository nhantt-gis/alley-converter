from pathlib import Path

import pyogrio

from alley_converter.config import ConverterConfig
from alley_converter.converter import convert_directory


def _write_csv(path: Path, rows: list[str]) -> None:
    path.write_text("id,name,geometry\n" + "\n".join(rows) + "\n", encoding="utf-8")


def test_convert_directory_writes_layers_and_combined_layer(tmp_path):
    data_dir = tmp_path / "data"
    output_path = data_dir / "alleys.gpkg"
    data_dir.mkdir()

    _write_csv(
        data_dir / "district_1.csv",
        ['1,main,"{""type"": ""Point"", ""coordinates"": [106.7, 10.8]}"'],
    )
    _write_csv(
        data_dir / "district_2.csv",
        ['2,side,"{""type"": ""Point"", ""coordinates"": [106.8, 10.9]}"'],
    )

    result = convert_directory(
        ConverterConfig(input_dir=data_dir, output_path=output_path, combined_layer="all_alleys")
    )

    assert output_path.exists()
    assert result.layer_counts == {"district_1": 1, "district_2": 1, "all_alleys": 2}
    assert set(pyogrio.list_layers(output_path)[:, 0]) == {
        "district_1",
        "district_2",
        "all_alleys",
    }


def test_convert_directory_skips_csv_without_geometry_column(tmp_path):
    data_dir = tmp_path / "data"
    output_path = data_dir / "alleys.gpkg"
    data_dir.mkdir()

    (data_dir / "bad.csv").write_text("id,name\n1,missing\n", encoding="utf-8")
    _write_csv(
        data_dir / "good.csv",
        ['1,main,"{""type"": ""Point"", ""coordinates"": [106.7, 10.8]}"'],
    )

    result = convert_directory(ConverterConfig(input_dir=data_dir, output_path=output_path))

    assert result.layer_counts == {"good": 1, "combined": 1}
    assert "bad.csv" in result.skipped_files
