"""Deprecated, use offical instead"""
from typing import Literal, TypedDict
from functools import total_ordering
import warnings

warnings.warn(
    "this file is deprecated, use offical `packaging.version` instead",
    DeprecationWarning, source=__file__)

__all__ = ("PR_VAILD", "PR_CASES", "PR_TYPE",
           "Version", "VersionJson", "parse")

type PR_VAILD = Literal["alpha", "beta", "hotfix", "rc", ""]

PR_CASE_DICT: dict[PR_VAILD, int] = {
    "alpha": 0,
    "beta": 1,
    "hotfix": 2,
    "rc": 3,
    "": 4,
}

PR_CASES: list[PR_VAILD] = list(PR_CASE_DICT.keys())


type PR_TYPE = tuple[PR_VAILD, int]


class VersionJson(TypedDict):
    major: int
    minor: int
    micro: int
    pr: PR_TYPE
    metadata: str


@total_ordering
class Version:
    def __init__(self,
                 major: int = 0,
                 minor: int = 0,
                 micro: int = 0,
                 pr: PR_TYPE | None = None,
                 metadata: str = ""
                 ) -> None:

        if pr is None:
            pr = ("", 0)

        assert pr, "how????"

        self.major: int = major
        self.minor: int = minor
        self.micro: int = micro
        self.pr: PR_TYPE = pr
        self.metadata: str = metadata

    def __str__(self) -> str:
        ver = f"v{self.major}.{self.minor}.{self.micro}"
        if self.pr[0] != "":
            ver += f"-{self.pr[0]}"

            if self.pr[1] != 0:
                ver += f"{self.pr[1]}"

        if self.metadata:
            ver += f"+{self.metadata}"

        return ver

    def __repr__(self) -> str:
        return (f"<Version(major={self.major}, minor={self.minor}, micro={self.micro}, "
                + f"pr={self.pr}, metadata={self.metadata})>")

    def __eq__(self, other) -> bool:
        if not self._convertable(other):
            raise ValueError(
                f"{type(other).__name__} can't convert to {type(self).__name__}")

        if isinstance(other, str):
            other = self.from_string(other)

        return (self.version_code == other.version_code
                and self.pr[0] == other.pr[0]
                and self.pr[1] == other.pr[1])

    def __lt__(self, other) -> bool:
        if not self._convertable(other):
            raise ValueError(
                f"{type(other).__name__} can't convert to {type(self).__name__}")

        if isinstance(other, str):
            other = self.from_string(other)

        # case 0: smaller version
        if self.version_code != other.version_code:
            return self.version_code < other.version_code

        # equal in normal

        # case 1: pr vs no pr
        self_case = PR_CASE_DICT[self.pr[0]]
        other_case = PR_CASE_DICT[other.pr[0]]
        if self_case != other_case:
            return self_case < other_case

        # case 2: pr vs pr
        return self.pr[1] < other.pr[1]

    def _convertable(self, v, /) -> bool:
        return isinstance(v, str | Version)

    @classmethod
    def from_string(cls, version: str) -> 'Version':
        return parse(version)

    def to_string(self) -> str:
        return str(self)

    @classmethod
    def from_json(cls, version: VersionJson) -> 'Version':
        try:
            return cls(**version)
        except TypeError as e:
            raise ValueError(
                f"the version is not a json value, current: {version}, type: {type(version).__name__}"
            ) from e

    def to_json(self) -> VersionJson:
        return {
            "major": self.major,
            "minor": self.minor,
            "micro": self.micro,
            "pr": self.pr,
            "metadata": self.metadata
        }

    version_code = property(lambda self: (
        self.major, self.minor, self.micro), doc="tuple[int, int, int]")


def parse(version) -> Version:
    if not isinstance(version, str):
        raise NotImplementedError

    # remove vV prefix
    version = version.lstrip("vV")

    if not version:
        return Version()

    splited = version.split(".", 2)
    major, minor, micro_pr_md = splited + ["0"] * (3 - len(splited))

    if not major.isdigit():
        raise ValueError(f"major is not a digit, current major: {major}")

    if not minor.isdigit():
        raise ValueError(f"minor is not a digit, current minor: {minor}")

    splited = micro_pr_md.split("+", 1)
    micro_pr, md = splited + [""] * (2 - len(splited))

    splited = micro_pr.split("-", 1)
    micro, prcase_prnum = splited + [""] * (2 - len(splited))

    if not micro.isdigit():
        raise ValueError(f"micro is not a digit, current micro: {micro}")

    splited = prcase_prnum.split(".", 1)
    prcase, prnum = splited + ["0"] * (2 - len(splited))

    if prcase not in PR_CASES:
        raise ValueError(
            f"pre-release is invalid, current pre-release: {prcase}")

    if not prnum.isdigit():
        raise ValueError(f"pre-release num is not a digit, current: {prnum}")

    return Version(
        int(major),
        int(minor),
        int(micro),
        (prcase, int(prnum)),
        md
    )
