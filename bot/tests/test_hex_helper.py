"""
test for hex_helper
"""

import pytest
from utils.hex_helper import normalize_hex_color, to_color_int, rgba_to_rgb


class TestNormalizeHexColor:
    def test_integer_input(self):
        assert normalize_hex_color(0xFF0000) == "FF0000"
        assert normalize_hex_color(0x00FF00) == "00FF00"
        assert normalize_hex_color(0x0000FF) == "0000FF"

    def test_string_input(self):
        assert normalize_hex_color("#FF0000") == "FF0000"
        assert normalize_hex_color("FF0000") == "FF0000"
        assert normalize_hex_color("0xFF0000") == "FF0000"
        assert normalize_hex_color("red") == "000000"

    def test_short_format(self):
        assert normalize_hex_color("#F00") == "FF0000"
        assert normalize_hex_color("ABC") == "AABBCC"


    @pytest.mark.parametrize(
        "input_str,expected",
        [
            ("#FF0000", "FF0000"),
            ("0xFF0000", "FF0000"),
            ("FF0000", "FF0000"),
            ("ff0000", "FF0000"),
            ("#ff0000", "FF0000"),
            ("   #FF0000   ", "FF0000"),
            ("0F0", "00FF00"),
            ("#040", "004400"),
            ("#086", "008866"),
            ("0x0fe", "00FFEE"),
            ("abc", "AABBCC"),

        ],
    )
    def test_various_formats(self, input_str, expected):
        assert normalize_hex_color(input_str) == expected

class TestRgbaToRgb:
    def test_int_rgba_input(self):
        assert rgba_to_rgb(0xFF000000) == "FFFFFF"
        assert rgba_to_rgb(0xFF0000FF) == "FF0000"
        assert rgba_to_rgb(0xFF000080) == "FF7F7F"

    def test_int_rgba_in_diff_bg(self):
        assert rgba_to_rgb(0xFF000080, 0xFFFFFF) == "FF7F7F"
        assert rgba_to_rgb(0xFF000080, 0x000000) == "800000"
        assert rgba_to_rgb(0xFF0000FF, 0xFFFFFF) == "FF0000"


    def test_rgba_white_background(self):
        result = rgba_to_rgb("#FF000080", "#FFFFFF")

        assert result == "FF7F7F"

    def test_rgba_black_background(self):
        result = rgba_to_rgb("#FF000080", "#000000")
        assert result == "800000"

    def test_fully_opaque(self):
        result = rgba_to_rgb("#FF0000FF", "#FFFFFF")
        assert result == "FF0000"

    def test_fully_transparent(self):
        result = rgba_to_rgb("#FF000000", "#00FF00")
        assert result == "00FF00"

    def unexpected_formats(self):
        assert rgba_to_rgb("invalid", "FFFFFF") == "000000"
        assert rgba_to_rgb("#FF0000", "invalid") == "000000"
        assert rgba_to_rgb("hello", "world") == "000000"

    @pytest.mark.parametrize(
        "rgba,bg,expected",
        [
            ("#FF000080", "#FFFFFF", "FF7F7F"),
            ("#00FF0080", "#FFFFFF", "7FFF7F"),
            ("#0000FF80", "#FFFFFF", "7F7FFF"),
            ("#FF000080", "#000000", "800000"),
            ("#FF0000FF", "#000000", "FF0000"),
        ],
    )
    def test_parameterized(self, rgba, bg, expected):
        assert rgba_to_rgb(rgba, bg) == expected

    class TestRgbaToRbgShort:
        def test_short_rgb(self):

            result = normalize_hex_color("FF0")
            assert result == "FFFF00"

        def test_rgba_white_bg(self):

            result = rgba_to_rgb("fa0b", "FF0000")
            assert result == "FF7D00"

        @pytest.mark.parametrize(
            "rgba,bg,excepted",
            [
                ("fff8", "fff", "FFFFFF"),
                ("f80f", "#fff", "FF8800"),
                ("f08c", "FFFFFF", "FF33A0"),
                ("fabc", "fda", "FFB4B8"),
                ("0104", "#FF8800", "BB6800"),
            ],
        )
        def test_short_rgba(self, rgba, bg, excepted):
            assert rgba_to_rgb(rgba, bg) == excepted

class TestToColorInt:
    def test_valid_hex(self):
        assert to_color_int("FF0000") == 0xFF0000
        assert to_color_int("#00FF00") == 0x00FF00
        assert to_color_int("0x0000FF") == 0x0000FF

    def formatted_int_input(self):
        assert to_color_int(0xAAFF0000) == 0xFF0000
        assert to_color_int(0xF) == 0x00000F
        assert to_color_int(0xD0000FF) == 0x0000FF

    def unexpected_formats(self):
        assert to_color_int("red") == 0x000000
        assert to_color_int("12345") == 0x000000
        assert to_color_int("#GGGGGG") == 0x000000
