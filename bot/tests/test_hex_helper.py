# tests/test_hex_helper.py
import pytest
from ..utils.hex_helper import normalize_hex_color, rgba_to_rgb


class TestNormalizeHexColor:
    """测试 normalize_hex_color 函数"""

    def test_integer_input(self):
        """测试整数输入"""
        assert normalize_hex_color(0xFF0000) == "FF0000"
        assert normalize_hex_color(0x00FF00) == "00FF00"
        assert normalize_hex_color(0x0000FF) == "0000FF"

    def test_string_input(self):
        """测试字符串输入"""
        assert normalize_hex_color("#FF0000") == "FF0000"
        assert normalize_hex_color("FF0000") == "FF0000"
        assert normalize_hex_color("0xFF0000") == "FF0000"
        assert normalize_hex_color("red") == "000000"  # 无效输入返回默认

    def test_short_format(self):
        """测试缩写格式"""
        assert normalize_hex_color("#F00") == "FF0000"  # RGB -> RRGGBB
        assert normalize_hex_color("ABC") == "AABBCC"

    @pytest.mark.parametrize("input_str,expected", [
        ("#FF0000", "FF0000"),
        ("0xFF0000", "FF0000"),
        ("FF0000", "FF0000"),
        ("ff0000", "FF0000"),  # 小写转大写
        ("#ff0000", "FF0000"),
        ("   #FF0000   ", "FF0000"),  # 去除空格
    ])
    def test_various_formats(self, input_str, expected):
        """测试各种格式"""
        assert normalize_hex_color(input_str) == expected


class TestRgbaToRgb:
    """测试 rgba_to_rgb 函数"""

    def test_rgba_white_background(self):
        """测试白色背景下的RGBA转换"""
        # 50%透明的红色在白色背景上
        result = rgba_to_rgb("#FF000080", "#FFFFFF")
        # 应该是粉红色
        assert result == "FF7F7F"

    def test_rgba_black_background(self):
        """测试黑色背景下的RGBA转换"""
        # 50%透明的红色在黑色背景上
        result = rgba_to_rgb("#FF000080", "#000000")
        assert result == "800000"

    def test_fully_opaque(self):
        """测试完全不透明"""
        result = rgba_to_rgb("#FF0000FF", "#FFFFFF")
        assert result == "FF0000"  # 完全不透明，背景不影响

    def test_fully_transparent(self):
        """测试完全透明"""
        result = rgba_to_rgb("#FF000000", "#00FF00")
        assert result == "00FF00"  # 完全透明，显示背景色

    @pytest.mark.parametrize("rgba,bg,expected", [
        ("#FF000080", "#FFFFFF", "FF7F7F"),
        ("#00FF0080", "#FFFFFF", "7FFF7F"),
        ("#0000FF80", "#FFFFFF", "7F7FFF"),
        ("#FF000080", "#000000", "800000"),
        ("#FF0000FF", "#000000", "FF0000"),
    ])
    def test_parameterized(self, rgba, bg, expected):
        """参数化测试多个组合"""
        assert rgba_to_rgb(rgba, bg) == expected

    class TestRgbaToRbgShort:
        """
        测试 简短版rgb与rgba
        """

        def test_short_rgb(self):
            """ 短的 rgb 转化 """
            result = normalize_hex_color("FF0")
            assert result == "FFFF00"

        @pytest.mark.parametrize("input_str,excepted", [
            ("0F0", "00FF00"),
            ("#040", "004400"),
            ("#086", "008866"),
            ("0x0fe", "00FFEE"),
            ("abc", "AABBCC"),
        ])
        def test_short_format(self, input_str, excepted):
            assert normalize_hex_color(input_str) == excepted

        def test_rgba_white_bg(self):
            """ 测试短的rgba转成rgb """
            result = rgba_to_rgb("fa0b", "FF0000")
            assert result == "FF7D00"

        @pytest.mark.parametrize("rgba,bg,excepted", [
            ("fff8", "fff", "FFFFFF"),
            ("f80f", "#fff", "FF8800"),
            ("f08c", "FFFFFF", "FF33A0"),
            ("fabc", "fda", "FFB4B8"),
            ("0104", "#FF8800", "BB6800")
        ])
        def test_short_rgba(self, rgba, bg, excepted):
            """ 批量测试 """
            assert rgba_to_rgb(rgba, bg) == excepted
