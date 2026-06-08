"""Kiss static coverage for render registry modules."""

import pytest

import rich._align_registry
import rich._color_blend_registry as blend_registry
import rich._color_system
import rich._control_registry
import rich._log_render_registry
import rich._markup_registry as markup_registry
import rich._segment_registry
import rich._style_registry
import rich._styled_registry
import rich._text_registry

rich._align_registry.register_align
rich._align_registry.align_class
rich._styled_registry.register_styled
rich._styled_registry.styled_class
rich._markup_registry.register_render_markup
rich._markup_registry.get_render_markup
rich._log_render_registry.register_log_render
rich._log_render_registry.log_render_class
rich._control_registry.register_control
rich._control_registry.control_class
rich._color_blend_registry.register_blend_rgb
rich._color_blend_registry.get_blend_rgb
rich._segment_registry.register_segment
rich._segment_registry.segment_class
rich._style_registry.register_style
rich._style_registry.style_class
rich._text_registry.register_text
rich._text_registry.get_text_class
rich._color_system.ColorSystem


def test_render_registry_static_refs():
    from rich._align_registry import align_class, register_align
    from rich._color_blend_registry import get_blend_rgb, register_blend_rgb
    from rich._color_system import ColorSystem
    from rich._control_registry import control_class, register_control
    from rich._log_render_registry import log_render_class, register_log_render
    from rich._markup_registry import get_render_markup, register_render_markup
    from rich._segment_registry import register_segment, segment_class
    from rich._style_registry import register_style, style_class
    from rich._styled_registry import register_styled, styled_class
    from rich._text_registry import get_text_class, register_text
    from rich.align import Align
    from rich.color import blend_rgb
    from rich.control import Control
    from rich.markup import render_markup
    from rich.segment import Segment
    from rich.style import Style
    from rich.styled import Styled
    from rich.text import Text
    from rich._log_render import LogRender

    register_align(Align)
    register_styled(Styled)
    register_render_markup(render_markup)
    register_log_render(LogRender)
    register_control(Control)
    register_blend_rgb(blend_rgb)
    register_segment(Segment)
    register_style(Style)
    register_text(Text)
    align_class()
    styled_class()
    get_render_markup()
    log_render_class()
    control_class()
    segment_class()
    style_class()
    get_text_class()
    get_blend_rgb()
    ColorSystem.STANDARD


def test_blend_registry_module_refs():
    blend_registry.register_blend_rgb
    blend_registry.get_blend_rgb


def test_markup_registry_module_refs():
    markup_registry.register_render_markup
    markup_registry.get_render_markup


def test_markup_helper_refs():
    from rich.markup import _render_with_tags, _render_without_tags, render_markup

    render_markup
    _render_without_tags
    _render_with_tags


def test_text_registry_not_registered():
    import rich._text_registry as registry

    old = registry._text_class
    registry._text_class = None
    try:
        with pytest.raises(RuntimeError, match="Text not registered"):
            registry.get_text_class()
    finally:
        registry._text_class = old


def test_segment_registry_not_registered():
    import rich._segment_registry as registry

    old = registry._segment_class
    registry._segment_class = None
    try:
        with pytest.raises(RuntimeError, match="Segment not registered"):
            registry.segment_class()
    finally:
        registry._segment_class = old


def test_style_registry_not_registered():
    import rich._style_registry as registry

    old = registry._style_class
    registry._style_class = None
    try:
        with pytest.raises(RuntimeError, match="Style not registered"):
            registry.style_class()
    finally:
        registry._style_class = old


def test_segment_isinstance():
    from rich._segment_proxy import Segment, segment_isinstance, segment_type
    from rich.segment import Segment as RealSegment

    assert segment_isinstance(RealSegment("hello"))
    assert not segment_isinstance("hello")
    assert RealSegment("x") == Segment("x")
    assert segment_type() is RealSegment
