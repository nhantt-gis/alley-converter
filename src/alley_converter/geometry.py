"""Geometry parsing helpers."""

from __future__ import annotations

import json
from typing import Any

from shapely.geometry import shape
from shapely.geometry.base import BaseGeometry


def parse_geojson_geometry(value: Any) -> BaseGeometry | None:
    """Parse a GeoJSON geometry or Feature string into a Shapely geometry.

    Invalid, empty, or unsupported values return ``None`` so callers can decide
    whether to preserve the row with a null geometry or drop it.
    """

    if not isinstance(value, str) or not value.strip():
        return None

    try:
        data = json.loads(value)
    except json.JSONDecodeError:
        return None

    if not isinstance(data, dict):
        return None

    if data.get("type") == "Feature":
        data = data.get("geometry")

    if not isinstance(data, dict):
        return None

    try:
        return shape(data)
    except (AttributeError, KeyError, TypeError, ValueError):
        return None
