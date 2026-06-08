"""Unicode version resolution for cell table loading."""
from __future__ import annotations

import bisect
import os

from rich._unicode_data._versions import VERSIONS

VERSION_ORDER = sorted(tuple(map(int, version.split("."))) for version in VERSIONS)
VERSION_SET = frozenset(VERSIONS)


def _parse_version(version: str) -> tuple[int, int, int]:
    version_integers: tuple[int, ...]
    try:
        version_integers = tuple(map(int, version.split(".")))
    except ValueError:
        raise ValueError(
            f"unicode version string {version!r} is badly formatted"
        ) from None
    while len(version_integers) < 3:
        version_integers = version_integers + (0,)
    return version_integers[:3]  # type: ignore[return-value]


def resolve_unicode_version(unicode_version: str) -> str:
    if unicode_version == "auto":
        unicode_version = os.environ.get("UNICODE_VERSION", "latest")
        try:
            _parse_version(unicode_version)
        except ValueError:
            unicode_version = "latest"

    if unicode_version == "latest":
        return VERSIONS[-1]

    try:
        version_numbers = _parse_version(unicode_version)
    except ValueError:
        version_numbers = _parse_version(VERSIONS[-1])
    major, minor, patch = version_numbers
    version = f"{major}.{minor}.{patch}"
    if version in VERSION_SET:
        return version
    insert_position = bisect.bisect_left(VERSION_ORDER, version_numbers)
    return VERSIONS[max(0, insert_position - 1)]
