from __future__ import annotations
import re
import pytest
from app.api.endpoints.farm import _validate_geojson_polygon

def test_polygon_validation_valid():
    # Valid closed polygon (square in WGS84 coordinates)
    valid_geojson = {
        "type": "Polygon",
        "coordinates": [
            [
                [72.15, 21.76],
                [72.16, 21.76],
                [72.16, 21.77],
                [72.15, 21.77],
                [72.15, 21.76],
            ]
        ],
    }
    is_valid, msg, area_acres = _validate_geojson_polygon(valid_geojson)
    assert is_valid is True
    assert msg == "Valid"
    assert area_acres is not None
    assert area_acres > 0

def test_polygon_validation_unclosed_rejected():
    unclosed_geojson = {
        "type": "Polygon",
        "coordinates": [
            [
                [72.15, 21.76],
                [72.16, 21.76],
                [72.16, 21.77],
                [72.15, 21.77],
            ]
        ],
    }
    is_valid, msg, area_acres = _validate_geojson_polygon(unclosed_geojson)
    assert is_valid is False
    assert "not closed" in msg.lower()
    assert area_acres is None

def test_polygon_validation_out_of_bounds_rejected():
    invalid_coords_geojson = {
        "type": "Polygon",
        "coordinates": [
            [
                [195.0, 21.76],
                [195.1, 21.76],
                [195.1, 21.77],
                [195.0, 21.77],
                [195.0, 21.76],
            ]
        ],
    }
    is_valid, msg, area_acres = _validate_geojson_polygon(invalid_coords_geojson)
    assert is_valid is False
    assert "out of bounds" in msg.lower()

def test_expert_severity_regex_parsing():
    # Test our regex extraction for severity from various strings
    test_cases = [
        ("Moderate (32%)", 32.0),
        ("75.5%", 75.5),
        ("High (80)", 80.0),
        ("45", 45.0),
    ]
    for raw_str, expected in test_cases:
        match = re.search(r"(\d+(?:\.\d+)?)", raw_str)
        assert match is not None
        val = float(match.group(1))
        assert val == expected

