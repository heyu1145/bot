"""
test for utils
"""
import pytest
from typing import Literal
from discord import Embed
from utils.utils import human_like_join, maybe_coro, multi_set_fields


class TestJoin:
    """test human_like_join"""

    def test_normal_join(self):
        assert human_like_join(["a", "b", "c"]) == "a, b or c"
        assert human_like_join(["a", "b"]) == "a or b"
        assert (
            human_like_join(["bob", "alex", "mark"], final=" and ")
            == "bob, alex and mark"
        )

    def test_unusual_join(self):
        a = "hello world"
        assert human_like_join(a) is a
        assert human_like_join([a]) is a
        assert human_like_join((a)) is a

    @pytest.mark.parametrize(
            "iterable,excepted",
            [
                ([], ""),
                ((), ""),
                (set(), ""),
                (["a"], "a"),
                (["a", "b"], "a or b"),
                (["a", "b", "c"], "a, b or c"),
            ],
            )
    def test_parametrize(self, iterable, excepted):
        assert human_like_join(iterable) == excepted


class TestCoro:
    """test maybe_coro"""

    def _test1(self) -> Literal["abc"]:
        return "abc"

    async def _test2(self) -> Literal[1]:
        return 1

    def _test3[T](self, a: T) -> T:
        return a

    async def _test4[T](self, a: T) -> T:
        return a

    async def test_normal_maybe_coro(self):
        assert await maybe_coro(self._test1) == "abc"
        assert await maybe_coro(self._test2) == 1
        assert await maybe_coro(self._test3, 1) == 1
        assert await maybe_coro(self._test4, a="hello world") == "hello world"

    async def test_lambda(self):
        assert await maybe_coro(lambda: 1) == 1
        assert await maybe_coro(lambda x: x, "a") == "a"

class TestMultiSetFields:
    """test multi_set_fields"""

    def test_multi_set_fields(self):
        embed = Embed()
        seted_embed = multi_set_fields(
            embed,
            False,
            True,
            False,
            a=1,
            b="hello",
            c=[1, 2, 3],
            d={"key": "value"},
            e=None,
        )
        assert isinstance(seted_embed, Embed)
        assert seted_embed == embed and seted_embed is embed
        assert len(seted_embed.fields) == 5
        f0, f1, f2, f3, f4 = seted_embed.fields
        assert f0.name == "a" and f0.value == "1"
        assert f1.name == "b" and f1.value == "hello"
        assert f2.name == "c" and f2.value == "[1, 2, 3]"
        assert f3.name == "d" and f3.value == "{'key': 'value'}"
        assert f4.name == "e" and f4.value == "None"
        assert not all(f.inline for f in seted_embed.fields)

    def unusual_multi_set_fields(self):
        fields = {
            "a": bytearray(b"hello"),
            "b": "hello",
            "c": 1+1j,
            "d": {"key": "value"},
            "e": Ellipsis,
            "f": frozenset({1, 2, 3}),
            "g": globals(),
            "h": (1, 2, 3),
            "i": iter([1,2,3]),
            "j": lambda x: x,
            "k": {"key": "value"}.keys(),
            "l": [1,2,3],
            "m": map(lambda x: x, [1,2,3]),
            "n": next,
            "o": b"bytes",
            "p": self,
            "q": memoryview(b"memory"),
            "r": range(5),
            "s": slice(1, 10, 2),
            "t": type,
            "u": u"unicode",
            "v": {"key": "value"}.values(),
            "w": Warning,
            "x": None,
            "y": ...,
            "z": NotImplemented,
        }
        embed = Embed()
        pytest.raises(ValueError, multi_set_fields, embed, False, True, False, **fields)
