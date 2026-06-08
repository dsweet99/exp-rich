"""Tests for the stdlib-only highlight kernel."""
import types

import pytest

from rich._highlight_kernel import (
    is_text_instance,
    make_text,
    register_text_types,
    span_class,
    text_class,
)
from rich.text import Span, Text


def test_register_and_make_text():
    register_text_types(Text, Span)
    assert text_class() is Text
    assert span_class() is Span
    made = make_text("hello")
    assert isinstance(made, Text)
    assert made.plain == "hello"


def test_is_text_instance_with_registered_text():
    register_text_types(Text, Span)
    text = Text("x")
    assert is_text_instance(text) is True
    assert is_text_instance("not text") is False


def test_is_text_instance_duck_typed():
    fake = types.SimpleNamespace(
        plain="a",
        copy=lambda: fake,
        highlight_regex=lambda *args, **kwargs: None,
    )
    assert is_text_instance(fake) is True


def test_text_class_not_registered():
    import rich._highlight_kernel as kernel

    old_text, old_span = kernel._text_class, kernel._span_class
    kernel._text_class = None
    kernel._span_class = None
    try:
        with pytest.raises(RuntimeError, match="Text class not registered"):
            text_class()
        with pytest.raises(RuntimeError, match="Span class not registered"):
            span_class()
        with pytest.raises(RuntimeError, match="Text class not registered"):
            make_text("x")
    finally:
        kernel._text_class = old_text
        kernel._span_class = old_span
        register_text_types(Text, Span)


def test_highlighter_call_with_str():
    from rich.highlighter import ReprHighlighter

    result = ReprHighlighter()("True")
    assert isinstance(result, Text)
    assert any(span.style == "repr.bool_true" for span in result.spans)


def test_regex_highlighter_base_class():
    from rich.highlighter import RegexHighlighter

    class WordHighlighter(RegexHighlighter):
        highlights = [r"(?P<word>\bfoo\b)"]
        base_style = "test."

    text = Text("foo bar")
    WordHighlighter().highlight(text)
    assert len(text.spans) == 1
    assert text.spans[0].start == 0
    assert text.spans[0].end == 3
    assert text.spans[0].style.startswith("test.")


def test_highlighter_registry_roundtrip():
    from rich._highlighter_registry import (
        highlighter_base_class,
        path_highlighter_class,
        register_highlighters,
        repr_highlighter,
        repr_highlighter_class,
        regex_highlighter_class,
    )
    from rich.highlighter import Highlighter, RegexHighlighter, ReprHighlighter

    register_highlighters(
        base_class=Highlighter,
        repr_class=ReprHighlighter,
        repr_factory=ReprHighlighter,
        regex_class=RegexHighlighter,
    )
    assert highlighter_base_class() is Highlighter
    assert repr_highlighter_class() is ReprHighlighter
    assert regex_highlighter_class() is RegexHighlighter
    assert isinstance(repr_highlighter(), ReprHighlighter)
    path_cls = path_highlighter_class()
    assert issubclass(path_cls, RegexHighlighter)
    highlighted = path_cls()("/foo/bar.py")
    assert highlighted.plain == "/foo/bar.py"


def test_theme_registry_roundtrip():
    from rich._theme_registry import register_theme, theme_class
    from rich.theme import Theme

    register_theme(Theme)
    assert theme_class() is Theme
    assert isinstance(theme_class()(), Theme)


def test_screen_registry_roundtrip():
    from rich._console_types import Group
    from rich._group_registry import register_group
    from rich._screen_registry import register_screen, screen_class
    from rich.screen import Screen

    register_group(Group)
    register_screen(Screen)
    assert screen_class() is Screen
    assert isinstance(screen_class()(style=""), Screen)


def test_group_registry_roundtrip():
    from rich._console_types import Group
    from rich._group_registry import Group as GroupProxy, group, group_class, register_group

    register_group(Group)
    assert group_class() is Group
    assert group(fit=True) is not None
    assert isinstance(GroupProxy("a"), Group)


def test_group_decorator_roundtrip():
    from rich._console_types import Group
    from rich._group_registry import group

    @group()
    def _renderables():
        return [1, 2]

    result = _renderables()
    assert isinstance(result, Group)
    assert len(result.renderables) == 2


def test_group_registry_not_registered():
    import rich._group_registry as registry

    old_group = registry._group_class
    registry._group_class = None
    try:
        with pytest.raises(RuntimeError, match="Group not registered"):
            registry.group_class()
    finally:
        registry._group_class = old_group


def test_screen_registry_not_registered():
    import rich._screen_registry as registry

    old = registry._screen_class
    registry._screen_class = None
    try:
        with pytest.raises(RuntimeError, match="Screen not registered"):
            registry.screen_class()
    finally:
        registry._screen_class = old


def test_theme_registry_not_registered():
    import rich._theme_registry as registry

    old = registry._theme_class
    registry._theme_class = None
    try:
        with pytest.raises(RuntimeError, match="Theme not registered"):
            registry.theme_class()
    finally:
        registry._theme_class = old


def test_highlighter_registry_not_registered():
    import rich._highlighter_registry as registry

    old = (
        registry._highlighter_base_class,
        registry._repr_highlighter_class,
        registry._repr_highlighter_factory,
        registry._regex_highlighter_class,
    )
    registry._highlighter_base_class = None
    registry._repr_highlighter_class = None
    registry._repr_highlighter_factory = None
    registry._regex_highlighter_class = None
    try:
        with pytest.raises(RuntimeError, match="Highlighter not registered"):
            registry.highlighter_base_class()
        with pytest.raises(RuntimeError, match="ReprHighlighter not registered"):
            registry.repr_highlighter_class()
        with pytest.raises(RuntimeError, match="ReprHighlighter not registered"):
            registry.repr_highlighter()
        with pytest.raises(RuntimeError, match="RegexHighlighter not registered"):
            registry.regex_highlighter_class()
        with pytest.raises(RuntimeError, match="RegexHighlighter not registered"):
            registry.path_highlighter_class()
    finally:
        (
            registry._highlighter_base_class,
            registry._repr_highlighter_class,
            registry._repr_highlighter_factory,
            registry._regex_highlighter_class,
        ) = old


def test_color_system_values():
    from rich._color_system import ColorSystem

    assert ColorSystem.TRUECOLOR == 3
    assert str(ColorSystem.STANDARD) == "ColorSystem.STANDARD"


def test_render_registries_roundtrip():
    from rich.align import Align
    from rich.color import blend_rgb
    from rich.control import Control
    from rich.markup import render_markup
    from rich.styled import Styled
    from rich._align_registry import align_class, register_align
    from rich._color_blend_registry import get_blend_rgb, register_blend_rgb
    from rich._control_registry import control_class, register_control
    from rich._log_render_registry import log_render_class, register_log_render
    from rich._log_render import LogRender
    from rich._markup_registry import get_render_markup, register_render_markup
    from rich._styled_registry import register_styled, styled_class

    register_align(Align)
    register_styled(Styled)
    register_render_markup(render_markup)
    register_log_render(LogRender)
    register_control(Control)
    register_blend_rgb(blend_rgb)

    assert align_class() is Align
    assert styled_class() is Styled
    assert get_render_markup() is render_markup
    assert log_render_class() is LogRender
    assert control_class() is Control
    assert get_blend_rgb() is blend_rgb


@pytest.mark.parametrize(
    "registry_module, accessor, label",
    [
        ("rich._align_registry", "align_class", "Align"),
        ("rich._styled_registry", "styled_class", "Styled"),
        ("rich._markup_registry", "get_render_markup", "markup.render"),
        ("rich._log_render_registry", "log_render_class", "LogRender"),
        ("rich._control_registry", "control_class", "Control"),
        ("rich._color_blend_registry", "get_blend_rgb", "blend_rgb"),
    ],
)
def test_render_registries_not_registered(registry_module, accessor, label):
    import importlib

    registry = importlib.import_module(registry_module)
    state_key = {
        "rich._align_registry": "_align_class",
        "rich._styled_registry": "_styled_class",
        "rich._markup_registry": "_render_markup",
        "rich._log_render_registry": "_log_render_class",
        "rich._control_registry": "_control_class",
        "rich._color_blend_registry": "_blend_rgb",
    }[registry_module]
    old = getattr(registry, state_key)
    setattr(registry, state_key, None)
    try:
        with pytest.raises(RuntimeError, match=f"{label} not registered"):
            getattr(registry, accessor)()
    finally:
        setattr(registry, state_key, old)
