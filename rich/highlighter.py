from ._highlighter_base import Highlighter

_LAZY_EXPORTS = {
    "NullHighlighter",
    "RegexHighlighter",
    "ReprHighlighter",
    "JSONHighlighter",
    "ISO8601Highlighter",
}


def __getattr__(name: str):
    if name in _LAZY_EXPORTS:
        from . import _highlighter_exports as exports

        return getattr(exports, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted(list(globals()) + list(_LAZY_EXPORTS))


def _register_highlighters() -> None:
    from ._highlighter_exports import JSONHighlighter, RegexHighlighter, ReprHighlighter
    from ._highlighter_registry import register_highlighters
    from ._highlight_kernel import make_text
    from ._json_highlight import register_json_highlight

    register_highlighters(
        base_class=Highlighter,
        repr_class=ReprHighlighter,
        repr_factory=ReprHighlighter,
        regex_class=RegexHighlighter,
    )
    register_json_highlight(JSONHighlighter().__call__, make_text)


_register_highlighters()

__all__ = ["Highlighter", *_LAZY_EXPORTS]
