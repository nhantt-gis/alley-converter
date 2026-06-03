from alley_converter.geometry import parse_geojson_geometry


def test_parse_geojson_geometry_object():
    geometry = parse_geojson_geometry('{"type": "Point", "coordinates": [106.7, 10.8]}')

    assert geometry is not None
    assert geometry.geom_type == "Point"
    assert geometry.x == 106.7
    assert geometry.y == 10.8


def test_parse_geojson_feature_object():
    geometry = parse_geojson_geometry(
        '{"type": "Feature", "properties": {}, "geometry": '
        '{"type": "LineString", "coordinates": [[0, 0], [1, 1]]}}'
    )

    assert geometry is not None
    assert geometry.geom_type == "LineString"


def test_parse_invalid_geometry_returns_none():
    assert parse_geojson_geometry("not-json") is None
    assert parse_geojson_geometry("") is None
    assert parse_geojson_geometry('{"type": "Feature", "properties": {}}') is None
