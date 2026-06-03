"""CSV to GeoPackage conversion utilities for alley datasets."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("gtelmaps-alley-geodata-convert-tool")
except PackageNotFoundError:  # pragma: no cover - only happens in editable-free runs.
    __version__ = "0.0.0"
