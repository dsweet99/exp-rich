from __future__ import annotations

import zlib
from html import escape
from math import ceil
from typing import Callable, Dict, Iterable, List, NamedTuple, Optional, Tuple, TYPE_CHECKING

from .cells import cell_len
from ._pick import M_COLOR, M_SEGMENT, rich_module
from .style import Style
from .terminal_theme import SVG_EXPORT_THEME, TerminalTheme

if TYPE_CHECKING:
    from ._types import Console, Segment



def _Segment():
    return rich_module(M_SEGMENT).Segment


def _blend_rgb():
    return rich_module(M_COLOR).blend_rgb

def _svg_escape_text(text: str) -> str:
    return escape(text).replace(" ", "&#160;")

def _svg_make_tag(name: str, content: Optional[str] = None, **attribs: object) -> str:
    def stringify(value: object) -> str:
        if isinstance(value, float):
            return format(value, "g")
        return str(value)

    tag_attribs = " ".join(
        f'{k.lstrip("_").replace("_", "-")}="{stringify(v)}"' for k, v in attribs.items()
    )
    if content:
        return f"<{name} {tag_attribs}>{content}</{name}>"
    return f"<{name} {tag_attribs}/>"

def _svg_style_css(
    style: Style, theme: TerminalTheme, cache: Dict[Style, str]
) -> str:
    if style in cache:
        return cache[style]
    css_rules = []
    color = (
        theme.foreground_color
        if (style.color is None or style.color.is_default)
        else style.color.get_truecolor(theme)
    )
    bgcolor = (
        theme.background_color
        if (style.bgcolor is None or style.bgcolor.is_default)
        else style.bgcolor.get_truecolor(theme)
    )
    if style.reverse:
        color, bgcolor = bgcolor, color
    if style.dim:
        color = _blend_rgb()(color, bgcolor, 0.4)
    css_rules.append(f"fill: {color.hex}")
    if style.bold:
        css_rules.append("font-weight: bold")
    if style.italic:
        css_rules.append("font-style: italic;")
    if style.underline:
        css_rules.append("text-decoration: underline;")
    if style.strike:
        css_rules.append("text-decoration: line-through;")
    css = ";".join(css_rules)
    cache[style] = css
    return css

def _svg_unique_id(
    segments: Iterable[Segment], title: str, unique_id: Optional[str]
) -> str:
    if unique_id is not None:
        return unique_id
    segment_repr = "".join(repr(segment) for segment in segments)
    return "terminal-" + str(
        zlib.adler32(
            segment_repr.encode("utf-8", "ignore") + title.encode("utf-8", "ignore")
        )
    )

def _svg_render_line_text(
    text: str,
    style: Style,
    x: int,
    y: int,
    theme: TerminalTheme,
    classes: Dict[str, int],
    char_width: float,
    line_height: float,
    char_height: float,
    unique_id: str,
    make_tag: Callable[..., str],
    escape_text: Callable[[str], str],
    get_svg_style: Callable[[Style], str],
    style_no: int,
) -> Tuple[List[str], List[str], int]:
    """Render one styled text run within an SVG line."""
    backgrounds: List[str] = []
    texts: List[str] = []
    rules = get_svg_style(style)
    if rules not in classes:
        classes[rules] = style_no
        style_no += 1
    class_name = f"r{classes[rules]}"
    if style.reverse:
        background = (
            theme.foreground_color.hex
            if style.color is None
            else style.color.get_truecolor(theme).hex
        )
        has_background = True
    else:
        bgcolor = style.bgcolor
        has_background = bgcolor is not None and not bgcolor.is_default
        background = (
            theme.background_color.hex
            if style.bgcolor is None
            else style.bgcolor.get_truecolor(theme).hex
        )
    text_length = cell_len(text)
    if has_background:
        backgrounds.append(
            make_tag(
                "rect",
                fill=background,
                x=x * char_width,
                y=y * line_height + 1.5,
                width=char_width * text_length,
                height=line_height + 0.25,
                shape_rendering="crispEdges",
            )
        )
    if text != " " * len(text):
        texts.append(
            make_tag(
                "text",
                escape_text(text),
                _class=f"{unique_id}-{class_name}",
                x=x * char_width,
                y=y * line_height + char_height,
                textLength=char_width * len(text),
                clip_path=f"url(#{unique_id}-line-{y})",
            )
        )
    return backgrounds, texts, style_no

def _svg_render_lines(
    segments: Iterable[Segment],
    width: int,
    theme: TerminalTheme,
    classes: Dict[str, int],
    char_width: float,
    line_height: float,
    char_height: float,
    unique_id: str,
    make_tag: Callable[..., str],
    escape_text: Callable[[str], str],
    get_svg_style: Callable[[Style], str],
) -> Tuple[List[str], List[str], int]:
    text_backgrounds: List[str] = []
    text_group: List[str] = []
    style_no = len(classes) + 1
    y = 0
    Segment = _Segment()
    for y, line in enumerate(Segment.split_and_crop_lines(segments, length=width)):
        x = 0
        for text, style, _control in line:
            style = style or Style()
            backgrounds, texts, style_no = _svg_render_line_text(
                text,
                style,
                x,
                y,
                theme,
                classes,
                char_width,
                line_height,
                char_height,
                unique_id,
                make_tag,
                escape_text,
                get_svg_style,
                style_no,
            )
            text_backgrounds.extend(backgrounds)
            text_group.extend(texts)
            x += cell_len(text)
    return text_backgrounds, text_group, y

def _svg_clip_lines(
    unique_id: str,
    line_offsets: List[float],
    char_width: float,
    width: int,
    line_height: float,
    make_tag: Callable[..., str],
) -> str:
    return "\n".join(
        f"""<clipPath id="{unique_id}-line-{line_no}">
    {make_tag("rect", x=0, y=offset, width=char_width * width, height=line_height + 0.25)}
            </clipPath>"""
        for line_no, offset in enumerate(line_offsets)
    )

def _svg_chrome(
    theme: TerminalTheme,
    unique_id: str,
    title: str,
    terminal_width: float,
    terminal_height: float,
    margin_left: float,
    margin_top: float,
    char_height: float,
    make_tag: Callable[..., str],
    escape_text: Callable[[str], str],
) -> str:
    chrome = make_tag(
        "rect",
        fill=theme.background_color.hex,
        stroke="rgba(255,255,255,0.35)",
        stroke_width="1",
        x=margin_left,
        y=margin_top,
        width=terminal_width,
        height=terminal_height,
        rx=8,
    )
    if title:
        chrome += make_tag(
            "text",
            escape_text(title),
            _class=f"{unique_id}-title",
            fill=theme.foreground_color.hex,
            text_anchor="middle",
            x=terminal_width // 2,
            y=margin_top + char_height + 6,
        )
    return chrome + """
            <g transform="translate(26,22)">
            <circle cx="0" cy="0" r="7" fill="#ff5f57"/>
            <circle cx="22" cy="0" r="7" fill="#febc2e"/>
            <circle cx="44" cy="0" r="7" fill="#28c840"/>
            </g>
        """

def _svg_format_document(
    *,
    code_format: str,
    unique_id: str,
    char_width: float,
    char_height: float,
    line_height: float,
    width: int,
    y: int,
    terminal_width: float,
    terminal_height: float,
    margin_width: int,
    margin_height: int,
    margin_left: int,
    margin_top: int,
    padding_left: int,
    padding_top: int,
    styles: str,
    chrome: str,
    text_backgrounds: List[str],
    text_group: List[str],
    lines: str,
) -> str:
    return code_format.format(
        unique_id=unique_id,
        char_width=char_width,
        char_height=char_height,
        line_height=line_height,
        terminal_width=char_width * width - 1,
        terminal_height=(y + 1) * line_height - 1,
        width=terminal_width + margin_width,
        height=terminal_height + margin_height,
        terminal_x=margin_left + padding_left,
        terminal_y=margin_top + padding_top,
        styles=styles,
        chrome=chrome,
        backgrounds="".join(text_backgrounds),
        matrix="".join(text_group),
        lines=lines,
    )

def _svg_read_segments(console: "Console", clear: bool) -> List[Segment]:
    with console._record_buffer_lock:
        Segment = _Segment()
        segments = list(Segment.filter_control(console._record_buffer))
        if clear:
            console._record_buffer.clear()
    return segments

class _SvgLayout(NamedTuple):
    char_height: int
    char_width: float
    line_height: float
    margin_left: int
    margin_top: int
    margin_right: int
    margin_bottom: int
    padding_left: int
    padding_top: int
    padding_width: int
    padding_height: int
    margin_width: int
    margin_height: int

def _svg_layout(font_aspect_ratio: float) -> _SvgLayout:
    char_height = 20
    char_width = char_height * font_aspect_ratio
    line_height = char_height * 1.22
    margin_left = margin_top = 1
    margin_right = margin_bottom = 1
    padding_top, padding_right, padding_bottom, padding_left = 40, 8, 8, 8
    padding_width = padding_left + padding_right
    padding_height = padding_top + padding_bottom
    margin_width = margin_left + margin_right
    margin_height = margin_top + margin_bottom
    return _SvgLayout(
        char_height,
        char_width,
        line_height,
        margin_left,
        margin_top,
        margin_right,
        margin_bottom,
        padding_left,
        padding_top,
        padding_width,
        padding_height,
        margin_width,
        margin_height,
    )

def export_svg(
    console: "Console",
    *,
    title: str,
    theme: Optional[TerminalTheme],
    clear: bool,
    code_format: str,
    font_aspect_ratio: float,
    unique_id: Optional[str],
) -> str:
    _theme = theme or SVG_EXPORT_THEME
    width = console.width
    layout = _svg_layout(font_aspect_ratio)
    style_cache: Dict[Style, str] = {}
    classes: Dict[str, int] = {}
    make_tag = _svg_make_tag
    escape_text = _svg_escape_text

    segments = _svg_read_segments(console, clear)

    unique_id = _svg_unique_id(segments, title, unique_id)

    def get_svg_style(style: Style) -> str:
        return _svg_style_css(style, _theme, style_cache)

    text_backgrounds, text_group, y = _svg_render_lines(
        segments,
        width,
        _theme,
        classes,
        layout.char_width,
        layout.line_height,
        layout.char_height,
        unique_id,
        make_tag,
        escape_text,
        get_svg_style,
    )
    line_offsets = [line_no * layout.line_height + 1.5 for line_no in range(y)]
    lines = _svg_clip_lines(
        unique_id, line_offsets, layout.char_width, width, layout.line_height, make_tag
    )
    styles = "\n".join(
        f".{unique_id}-r{rule_no} {{ {css} }}" for css, rule_no in classes.items()
    )
    terminal_width = ceil(width * layout.char_width + layout.padding_width)
    terminal_height = (y + 1) * layout.line_height + layout.padding_height
    chrome = _svg_chrome(
        _theme,
        unique_id,
        title,
        terminal_width,
        terminal_height,
        layout.margin_left,
        layout.margin_top,
        layout.char_height,
        make_tag,
        escape_text,
    )
    return _svg_format_document(
        code_format=code_format,
        unique_id=unique_id,
        char_width=layout.char_width,
        char_height=layout.char_height,
        line_height=layout.line_height,
        width=width,
        y=y,
        terminal_width=terminal_width,
        terminal_height=terminal_height,
        margin_width=layout.margin_width,
        margin_height=layout.margin_height,
        margin_left=layout.margin_left,
        margin_top=layout.margin_top,
        padding_left=layout.padding_left,
        padding_top=layout.padding_top,
        styles=styles,
        chrome=chrome,
        text_backgrounds=text_backgrounds,
        text_group=text_group,
        lines=lines,
    )