from __future__ import annotations

from html import escape
from typing import Dict, List, Optional, TYPE_CHECKING

from ._export_format import CONSOLE_HTML_FORMAT
from ._pick import M_SEGMENT, rich_module
from .terminal_theme import DEFAULT_TERMINAL_THEME, TerminalTheme

if TYPE_CHECKING:
    from ._types import Console



def _Segment():
    return rich_module(M_SEGMENT).Segment

def _export_html_inline_fragments(
    segments, theme: TerminalTheme, append
) -> None:
    Segment = _Segment()
    for text, style, _ in Segment.filter_control(Segment.simplify(segments)):
        text = escape(text)
        if not style:
            append(text)
            continue
        rule = style.get_html_style(theme)
        if style.link:
            text = f'<a href="{style.link}">{text}</a>'
        append(f'<span style="{rule}">{text}</span>' if rule else text)

def _export_html_class_fragments(
    segments, theme: TerminalTheme, append
) -> str:
    styles: Dict[str, int] = {}
    Segment = _Segment()
    for text, style, _ in Segment.filter_control(Segment.simplify(segments)):
        text = escape(text)
        if not style:
            append(text)
            continue
        rule = style.get_html_style(theme)
        style_number = styles.setdefault(rule, len(styles) + 1)
        if style.link:
            text = f'<a class="r{style_number}" href="{style.link}">{text}</a>'
        else:
            text = f'<span class="r{style_number}">{text}</span>'
        append(text)
    stylesheet_rules: List[str] = []
    for style_rule, style_number in styles.items():
        if style_rule:
            stylesheet_rules.append(f".r{style_number} {{{style_rule}}}")
    return "\n".join(stylesheet_rules)

def console_export_html(
    console: "Console",
    *,
    theme: Optional[TerminalTheme] = None,
    clear: bool = True,
    code_format: Optional[str] = None,
    inline_styles: bool = False,
) -> str:
    assert console.record, (
        "To export console contents set record=True in the constructor or instance"
    )
    fragments: List[str] = []
    append = fragments.append
    _theme = theme or DEFAULT_TERMINAL_THEME
    render_code_format = CONSOLE_HTML_FORMAT if code_format is None else code_format

    with console._record_buffer_lock:
        if inline_styles:
            _export_html_inline_fragments(console._record_buffer, _theme, append)
            stylesheet = ""
        else:
            stylesheet = _export_html_class_fragments(
                console._record_buffer, _theme, append
            )
        rendered_code = render_code_format.format(
            code="".join(fragments),
            stylesheet=stylesheet,
            foreground=_theme.foreground_color.hex,
            background=_theme.background_color.hex,
        )
        if clear:
            del console._record_buffer[:]
    return rendered_code