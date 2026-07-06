"""
changelog modification
"""
from pathlib import Path
from typing import Literal
from packaging.version import parse, Version, InvalidVersion
import re

this_file = Path(__file__)
this_dict = this_file.parent
parents = this_file.parents
home_dict = Path.home()

trying_map = ["CHANGELOG.md", "changelog.md"]

__all__ = ("ChangelogType", "get_changelog",
           "split_changelog", "VersionChangelog", "InvalidVersion")

version_compile = re.compile(r"## \[((vV)?\d+\.\d+\.\d+(\-.+\.\d)?(\+.+)?)\]")
data_compile = re.compile(r"\- (.+)")
option_compile = re.compile(r"### ((Added)|(Changed)|(Fixed))")

type ChangelogType = Literal["Added", "Changed", "Fixed"]


def get_changelog(name: str | None = None) -> Path | None:
    """
    get the changelogs path
    """
    if not name:
        try_map = trying_map
    else:
        try_map = [name]
    try:
        this_dict.relative_to(home_dict)
    except ValueError:
        return None
    for path in parents:
        if path == home_dict:
            break

        for trying in try_map:
            try_path = path / trying

            if try_path.is_file():
                return try_path

    return None


class VersionChangelog:
    def __init__(self, version: Version, changelog: dict[ChangelogType, list[str]]) -> None:
        self.version = version
        self.changelog = changelog

    def __repr__(self) -> str:
        return f"<VersionChangelog(version={self.version}, changelog={self.changelog})>"


def find_changelog_version(line: str) -> Version | None:
    """
    find the changelogs version string
    """
    matched = version_compile.search(line)
    if matched:
        return parse(matched.group(1))

    return None


def split_data(version: Version, lines: list[str]) -> VersionChangelog:
    """
    split out all of the changelog
    """
    added: list[str] = []
    changed: list[str] = []
    fixed: list[str] = []

    current = added

    for line in lines:
        option = option_compile.match(line)
        data = data_compile.match(line)
        match option:
            case None:
                pass
            case _:
                match str(option.group(1)):
                    case "Added":
                        current = added
                    case "Changed":
                        current = changed
                    case "Fixed":
                        current = fixed

        match data:
            case None:
                pass
            case _:
                current.append(data.group(1))

    return VersionChangelog(
        version,
        {
            "Added": added,
            "Changed": changed,
            "Fixed": fixed
        }
    )


def split_changelog(file: Path) -> list[VersionChangelog] | None:
    """
    split changelogs data by changelog path
    """
    if not file.exists():
        raise FileNotFoundError("the path is not exists")

    if not file.is_file():
        raise ValueError("the path is not a file")

    response: list[Version] = []

    lines: list[str] = file.read_text().splitlines()
    changelogs_index: list[tuple[int, int]] = []
    start = 0

    for i, line in enumerate(lines):
        resp = find_changelog_version(line)
        if resp:
            if start:
                changelogs_index.append((start, i))
            start = i

            response.append(resp)

    changelogs_index.append((start, len(lines)))

    assert len(response) == len(
        changelogs_index), "unexpected error: changelog count not same as version count"

    result = []

    for i in range(len(response)):
        result.append(split_data(
            response[i], lines[changelogs_index[i][0]:changelogs_index[i][1] + 1]))

    return result
