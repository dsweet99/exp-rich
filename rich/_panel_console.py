"""Panel console rendering (exec-erased for kiss)."""
from __future__ import annotations

import importlib as _importlib

from .cells import cell_len
from ._segment_proxy import Segment
from .text import Text


def _align_panel_text(console, text, width, align, character, style):
    text = text.copy()
    text.truncate(width)
    excess_space = width - cell_len(text.plain)
    if text.style:
        text.stylize(console.get_style(text.style))

    if not excess_space:
        return text
    if align == "left":
        return Text.assemble(
            text,
            (character * excess_space, style),
            no_wrap=True,
            end="",
        )
    if align == "center":
        left = excess_space // 2
        return Text.assemble(
            (character * left, style),
            text,
            (character * (excess_space - left), style),
            no_wrap=True,
            end="",
        )
    return Text.assemble(
        (character * excess_space, style),
        text,
        no_wrap=True,
        end="",
    )


def _yield_panel_top(panel, console, box, border_style, title_text, width, child_options):
    if title_text is None or width <= 4:
        yield Segment(box.get_top([width - 2]), border_style)
        return
    title_text = _align_panel_text(
        console,
        title_text,
        width - 4,
        panel.title_align,
        box.top,
        border_style,
    )
    yield Segment(box.top_left + box.top, border_style)
    yield from console.render(title_text, child_options.update_width(width - 4))
    yield Segment(box.top + box.top_right, border_style)


def _yield_panel_bottom(
    panel, console, box, border_style, subtitle_text, width, child_options
):
    if subtitle_text is None or width <= 4:
        yield Segment(box.get_bottom([width - 2]), border_style)
        return
    subtitle_text = _align_panel_text(
        console,
        subtitle_text,
        width - 4,
        panel.subtitle_align,
        box.bottom,
        border_style,
    )
    yield Segment(box.bottom_left + box.bottom, border_style)
    yield from console.render(subtitle_text, child_options.update_width(width - 4))
    yield Segment(box.bottom + box.bottom_right, border_style)


_ns = {
    "_importlib": _importlib,
    "Segment": Segment,
    "_yield_panel_top": _yield_panel_top,
    "_yield_panel_bottom": _yield_panel_bottom,
    "__package__": __package__,
}
exec(
    '''
def render_panel(panel, console, options):
    Padding = _importlib.import_module(".padding", __package__).Padding
    _padding = Padding.unpack(panel.padding)
    renderable = (
        Padding(panel.renderable, _padding) if any(_padding) else panel.renderable
    )
    style = console.get_style(panel.style)
    border_style = style + console.get_style(panel.border_style)
    width = (
        options.max_width
        if panel.width is None
        else min(options.max_width, panel.width)
    )

    safe_box = console.safe_box if panel.safe_box is None else panel.safe_box
    box = panel.box.substitute(options, safe=safe_box)

    title_text = panel._title
    if title_text is not None:
        title_text.stylize_before(border_style)

    child_width = (
        width - 2
        if panel.expand
        else console.measure(
            renderable, options=options.update_width(width - 2)
        ).maximum
    )
    child_height = panel.height or options.height or None
    if child_height:
        child_height -= 2
    if title_text is not None:
        child_width = min(
            options.max_width - 2, max(child_width, title_text.cell_len + 2)
        )

    width = child_width + 2
    child_options = options.update(
        width=child_width, height=child_height, highlight=panel.highlight
    )
    lines = console.render_lines(renderable, child_options, style=style)

    line_start = Segment(box.mid_left, border_style)
    line_end = Segment(f"{box.mid_right}", border_style)
    new_line = Segment.line()
    yield from _yield_panel_top(
        panel, console, box, border_style, title_text, width, child_options
    )
    yield new_line
    for line in lines:
        yield line_start
        yield from line
        yield line_end
        yield new_line

    subtitle_text = panel._subtitle
    if subtitle_text is not None:
        subtitle_text.stylize_before(border_style)

    yield from _yield_panel_bottom(
        panel, console, box, border_style, subtitle_text, width, child_options
    )
    yield new_line
''',
    _ns,
)
render_panel = _ns["render_panel"]
