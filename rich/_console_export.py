"""Console HTML and SVG export helpers."""
from __future__ import annotations

import zlib
from html import escape
from math import ceil
from typing import TYPE_CHECKING, Dict, Iterable, List, Optional, Tuple

from .color import blend_rgb
from .segment import Segment
from .style import Style
from .terminal_theme import DEFAULT_TERMINAL_THEME, SVG_EXPORT_THEME, TerminalTheme

def _append_inline_html(fragments: List[str], segments: Iterable[Segment], theme: TerminalTheme) -> None:
    append = fragments.append
    for text, style, _ in segments:
        text = escape(text)
        if not style:
            append(text)
            continue
        rule = style.get_html_style(theme)
        if style.link:
            text = f'<a href="{style.link}">{text}</a>'
        append(f'<span style="{rule}">{text}</span>' if rule else text)

def _append_classed_html(fragments: List[str], segments: Iterable[Segment], theme: TerminalTheme) -> str:
    append = fragments.append
    styles: Dict[str, int] = {}
    for text, style, _ in segments:
        text = escape(text)
        if not style:
            append(text)
            continue
        rule = style.get_html_style(theme)
        style_number = styles.setdefault(rule, len(styles) + 1)
        if style.link:
            append(f'<a class="r{style_number}" href="{style.link}">{text}</a>')
        else:
            append(f'<span class="r{style_number}">{text}</span>')
    rules = [f'.r{style_number} {{{style_rule}}}' for style_rule, style_number in styles.items() if style_rule]
    return '\n'.join(rules)

def export_html_buffer(record_buffer: List[Segment], *, theme: Optional[TerminalTheme], code_format: str, inline_styles: bool) -> Tuple[str, str]:
    """Build HTML code and stylesheet from a record buffer."""
    fragments: List[str] = []
    _theme = theme or DEFAULT_TERMINAL_THEME
    segments = Segment.filter_control(Segment.simplify(record_buffer))
    if inline_styles:
        _append_inline_html(fragments, segments, _theme)
        stylesheet = ''
    else:
        stylesheet = _append_classed_html(fragments, segments, _theme)
    rendered = code_format.format(code=''.join(fragments), stylesheet=stylesheet, foreground=_theme.foreground_color.hex, background=_theme.background_color.hex)
    return (rendered, _theme.foreground_color.hex)

def _svg_style_for_segment(style: Style, theme: TerminalTheme, cache: Dict[Style, str]) -> str:
    if style in cache:
        return cache[style]
    css_rules = []
    color = theme.foreground_color if style.color is None or style.color.is_default else style.color.get_truecolor(theme)
    bgcolor = theme.background_color if style.bgcolor is None or style.bgcolor.is_default else style.bgcolor.get_truecolor(theme)
    if style.reverse:
        color, bgcolor = (bgcolor, color)
    if style.dim:
        color = blend_rgb(color, bgcolor, 0.4)
    css_rules.append(f'fill: {color.hex}')
    if style.bold:
        css_rules.append('font-weight: bold')
    if style.italic:
        css_rules.append('font-style: italic;')
    if style.underline:
        css_rules.append('text-decoration: underline;')
    if style.strike:
        css_rules.append('text-decoration: line-through;')
    css = ';'.join(css_rules)
    cache[style] = css
    return css

def _render_svg_line_cells(line: List[Segment], *, y: int, unique_id: str, theme: TerminalTheme, style_cache: Dict[Style, str], classes: Dict[str, int], style_no: int, char_width: float, line_height: float, char_height: float, make_tag, escape_text) -> Tuple[List[str], List[str], int]:
    from rich.cells import cell_len
    text_backgrounds: List[str] = []
    text_group: List[str] = []
    x = 0
    for text, line_style, _control in line:
        line_style = line_style or Style()
        rules = _svg_style_for_segment(line_style, theme, style_cache)
        if rules not in classes:
            classes[rules] = style_no
            style_no += 1
        class_name = f'r{classes[rules]}'
        if line_style.reverse:
            background = theme.foreground_color.hex if line_style.color is None else line_style.color.get_truecolor(theme).hex
            has_background = True
        else:
            bgcolor = line_style.bgcolor
            has_background = bgcolor is not None and (not bgcolor.is_default)
            background = theme.background_color.hex if line_style.bgcolor is None else line_style.bgcolor.get_truecolor(theme).hex
        text_length = cell_len(text)
        if has_background:
            text_backgrounds.append(make_tag('rect', fill=background, x=x * char_width, y=y * line_height + 1.5, width=char_width * text_length, height=line_height + 0.25, shape_rendering='crispEdges'))
        if text != ' ' * len(text):
            text_group.append(make_tag('text', escape_text(text), _class=f'{unique_id}-{class_name}', x=x * char_width, y=y * line_height + char_height, textLength=char_width * len(text), clip_path=f'url(#{unique_id}-line-{y})'))
        x += cell_len(text)
    return (text_backgrounds, text_group, style_no)

def _svg_escape_text(text: str) -> str:
    return escape(text).replace(" ", "&#160;")


def _svg_stringify(value: object) -> str:
    if isinstance(value, float):
        return format(value, "g")
    return str(value)


def _svg_make_tag(name: str, content: Optional[str] = None, **attribs: object) -> str:
    tag_attribs = " ".join(
        f'{k.lstrip("_").replace("_", "-")}="{_svg_stringify(v)}"'
        for k, v in attribs.items()
    )
    if content:
        return f"<{name} {tag_attribs}>{content}</{name}>"
    return f"<{name} {tag_attribs}/>"


def _svg_build_clip_lines(
    unique_id: str, line_offsets: List[float], char_width: float, width: int, line_height: float
) -> str:
    return "\n".join(
        f'<clipPath id="{unique_id}-line-{line_no}">\n    '
        f'{_svg_make_tag("rect", x=0, y=offset, width=char_width * width, height=line_height + 0.25)}\n'
        f"            </clipPath>"
        for line_no, offset in enumerate(line_offsets)
    )


def _svg_build_chrome(
    *,
    title: str,
    unique_id: str,
    theme: TerminalTheme,
    terminal_width: int,
    terminal_height: float,
    margin_left: int,
    margin_top: int,
    char_height: float,
) -> str:
    chrome = _svg_make_tag(
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
        chrome += _svg_make_tag(
            "text",
            _svg_escape_text(title),
            _class=f"{unique_id}-title",
            fill=theme.foreground_color.hex,
            text_anchor="middle",
            x=terminal_width // 2,
            y=margin_top + char_height + 6,
        )
    chrome += """
            <g transform="translate(26,22)">
            <circle cx="0" cy="0" r="7" fill="#ff5f57"/>
            <circle cx="22" cy="0" r="7" fill="#febc2e"/>
            <circle cx="44" cy="0" r="7" fill="#28c840"/>
            </g>
        """
    return chrome


def _svg_collect_rendered_lines(
    segments: List[Segment],
    *,
    width: int,
    unique_id: str,
    theme: TerminalTheme,
    style_cache: Dict[Style, str],
    char_width: float,
    line_height: float,
    char_height: float,
) -> tuple[List[str], List[str], Dict[str, int], int, int]:
    text_backgrounds: List[str] = []
    text_group: List[str] = []
    classes: Dict[str, int] = {}
    style_no = 1
    y = 0
    for y, line in enumerate(Segment.split_and_crop_lines(segments, length=width)):
        backgrounds, group, style_no = _render_svg_line_cells(
            line,
            y=y,
            unique_id=unique_id,
            theme=theme,
            style_cache=style_cache,
            classes=classes,
            style_no=style_no,
            char_width=char_width,
            line_height=line_height,
            char_height=char_height,
            make_tag=_svg_make_tag,
            escape_text=_svg_escape_text,
        )
        text_backgrounds.extend(backgrounds)
        text_group.extend(group)
    return text_backgrounds, text_group, classes, style_no, y


def _svg_layout_metrics() -> tuple[int, int, int, int, int, int, int, int]:
    margin_top = margin_right = margin_bottom = margin_left = 1
    padding_top, padding_right, padding_bottom, padding_left = (40, 8, 8, 8)
    padding_width = padding_left + padding_right
    padding_height = padding_top + padding_bottom
    margin_width = margin_left + margin_right
    margin_height = margin_top + margin_bottom
    return margin_width, margin_height, padding_width, padding_height, margin_left, margin_top, padding_left, padding_top


def _svg_unique_id(segments: List[Segment], title: str) -> str:
    payload = ''.join(repr(segment) for segment in segments).encode('utf-8', 'ignore') + title.encode('utf-8', 'ignore')
    return 'terminal-' + str(zlib.adler32(payload))


def export_svg_buffer(console: 'Console', record_buffer: List[Segment], *, title: str, theme: Optional[TerminalTheme], code_format: str, font_aspect_ratio: float, unique_id: Optional[str]) -> str:
    """Build SVG export string from a record buffer."""
    _theme = theme or SVG_EXPORT_THEME
    style_cache: Dict[Style, str] = {}
    width = console.width
    char_height = 20
    char_width = char_height * font_aspect_ratio
    line_height = char_height * 1.22
    margin_width, margin_height, padding_width, padding_height, margin_left, margin_top, padding_left, padding_top = _svg_layout_metrics()
    segments = list(Segment.filter_control(record_buffer))
    if unique_id is None:
        unique_id = _svg_unique_id(segments, title)
    text_backgrounds, text_group, classes, _style_no, y = _svg_collect_rendered_lines(
        segments,
        width=width,
        unique_id=unique_id,
        theme=_theme,
        style_cache=style_cache,
        char_width=char_width,
        line_height=line_height,
        char_height=char_height,
    )
    line_offsets = [line_no * line_height + 1.5 for line_no in range(y)]
    lines = _svg_build_clip_lines(unique_id, line_offsets, char_width, width, line_height)
    styles = "\n".join(f".{unique_id}-r{rule_no} {{ {css} }}" for css, rule_no in classes.items())
    backgrounds = "".join(text_backgrounds)
    matrix = "".join(text_group)
    terminal_width = ceil(width * char_width + padding_width)
    terminal_height = (y + 1) * line_height + padding_height
    chrome = _svg_build_chrome(
        title=title,
        unique_id=unique_id,
        theme=_theme,
        terminal_width=terminal_width,
        terminal_height=terminal_height,
        margin_left=margin_left,
        margin_top=margin_top,
        char_height=char_height,
    )
    return code_format.format(unique_id=unique_id, char_width=char_width, char_height=char_height, line_height=line_height, terminal_width=char_width * width - 1, terminal_height=(y + 1) * line_height - 1, width=terminal_width + margin_width, height=terminal_height + margin_height, terminal_x=margin_left + padding_left, terminal_y=margin_top + padding_top, styles=styles, chrome=chrome, backgrounds=backgrounds, matrix=matrix, lines=lines)
