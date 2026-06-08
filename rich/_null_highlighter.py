"""NullHighlighter (one concrete type per file for kiss)."""
from __future__ import annotations

from typing import Any

from ._highlighter_base import Highlighter


class NullHighlighter(Highlighter):
    """A highlighter object that doesn't highlight.

    May be used to disable highlighting entirely.

    """

    def highlight(self, text: Any) -> None:
        """Nothing to do"""
