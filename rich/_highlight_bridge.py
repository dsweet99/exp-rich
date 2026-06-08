"""Runtime bridge so modules can construct Text/Span without importing text."""

from typing import Any, Callable, Optional, Type

_text_class: Optional[Type[Any]] = None
_copy_text: Optional[Callable[[Any], Any]] = None
_span_class: Optional[Type[Any]] = None
_render_markup: Optional[Callable[..., Any]] = None
_escape_markup: Optional[Callable[[str], str]] = None
_normalize_panel_label: Optional[Callable[[Any], Any]] = None
_align_panel_border_label: Optional[Callable[..., Any]] = None


def configure(
    text_class: Type[Any],
    copy_text: Callable[[Any], Any],
    span_class: Optional[Type[Any]] = None,
) -> None:
    """Register Text helpers from rich.text once it is loaded."""
    global _text_class, _copy_text, _span_class
    _text_class = text_class
    _copy_text = copy_text
    _span_class = span_class


def configure_markup(
    render_fn: Callable[..., Any],
    escape: Callable[[str], str],
) -> None:
    """Register markup helpers from rich.markup once it is loaded."""
    global _render_markup, _escape_markup
    _render_markup = render_fn
    _escape_markup = escape


def configure_panel(
    normalize_label: Callable[[Any], Any],
    align_border_label: Callable[..., Any],
) -> None:
    """Register panel label helpers from rich.text once it is loaded."""
    global _normalize_panel_label, _align_panel_border_label
    _normalize_panel_label = normalize_label
    _align_panel_border_label = align_border_label


def text_from_str(value: str) -> Any:
    if _text_class is None:
        raise RuntimeError("rich.text has not registered the highlight bridge")
    return _text_class(value)


def text_create(*args: Any, **kwargs: Any) -> Any:
    if _text_class is None:
        raise RuntimeError("rich.text has not registered the highlight bridge")
    return _text_class(*args, **kwargs)


def copy_text(value: Any) -> Any:
    if _copy_text is None:
        raise RuntimeError("rich.text has not registered the highlight bridge")
    return _copy_text(value)


def make_span(start: int, end: int, style: Any) -> Any:
    if _span_class is None:
        raise RuntimeError("rich.text has not registered the highlight bridge")
    return _span_class(start, end, style)


def invoke_markup_render(*args: Any, **kwargs: Any) -> Any:
    if _render_markup is None:
        raise RuntimeError("rich.markup has not registered the highlight bridge")
    return _render_markup(*args, **kwargs)


def escape_markup(markup: str) -> str:
    if _escape_markup is None:
        raise RuntimeError("rich.markup has not registered the highlight bridge")
    return _escape_markup(markup)


def is_text(value: Any) -> bool:
    return _text_class is not None and isinstance(value, _text_class)


def normalize_panel_label(value: Any) -> Any:
    if _normalize_panel_label is None:
        raise RuntimeError("rich.text has not registered panel helpers")
    return _normalize_panel_label(value)


def align_panel_border_label(
    console: Any, text: Any, width: int, align: str, character: str, style: Any
) -> Any:
    if _align_panel_border_label is None:
        raise RuntimeError("rich.text has not registered panel helpers")
    return _align_panel_border_label(console, text, width, align, character, style)
