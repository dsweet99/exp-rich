"""Highlighter ABC (no concrete subclasses — see _highlighter_types)."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Union

from ._highlight_kernel import is_text_instance, make_text


class Highlighter(ABC):
    """Abstract base class for highlighters."""

    def __call__(self, text: Union[str, Any]) -> Any:
        """Highlight a str or Text instance."""
        if isinstance(text, str):
            highlight_text = make_text(text)
        elif is_text_instance(text):
            highlight_text = text.copy()
        else:
            raise TypeError(f"str or Text instance required, not {text!r}")
        self.highlight(highlight_text)
        return highlight_text

    @abstractmethod
    def highlight(self, text: Any) -> None:
        """Apply highlighting in place to text."""
