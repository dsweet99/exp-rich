from __future__ import annotations

from typing import Any, List, Optional, Union, TYPE_CHECKING

from .segment import Segment

if TYPE_CHECKING:
    from ._types import Console, ConsoleOptions, JustifyMethod, OverflowMethod, Style


def _print_normalize_objects(
    objects: tuple, end: str, new_line_type: type
) -> tuple:
    if objects:
        return objects
    if end == "\n":
        return (new_line_type(),)
    return ("",)

def _print_soft_wrap_options(
    console: "Console",
    soft_wrap: Optional[bool],
    no_wrap: Optional[bool],
    overflow: Optional["OverflowMethod"],
    crop: bool,
) -> tuple[Optional[bool], Optional["OverflowMethod"], bool]:
    if soft_wrap is None:
        soft_wrap = console.soft_wrap
    if not soft_wrap:
        return no_wrap, overflow, crop
    if no_wrap is None:
        no_wrap = True
    if overflow is None:
        overflow = "ignore"
    return no_wrap, overflow, False

def _print_collect_segments(
    console: "Console",
    renderables,
    render_options: "ConsoleOptions",
    style: Optional[Union[str, "Style"]],
) -> List[Segment]:
    new_segments: List[Segment] = []
    extend = new_segments.extend
    render = console.render
    if style is None:
        for renderable in renderables:
            extend(render(renderable, render_options))
        return new_segments

    render_style = console.get_style(style)
    new_line = Segment.line()
    for renderable in renderables:
        for line, add_new_line in Segment.split_lines_terminator(
            render(renderable, render_options)
        ):
            extend(Segment.apply_style(line, render_style))
            if add_new_line:
                new_segments.append(new_line)
    return new_segments

def _print_apply_new_line_start(new_segments: List[Segment]) -> None:
    if len("".join(segment.text for segment in new_segments).splitlines()) <= 1:
        return
    new_segments.insert(0, Segment.line())

def _print_buffer_segments(
    console: "Console", new_segments: List[Segment], crop: bool
) -> None:
    if crop:
        buffer_extend = console._buffer.extend
        for line in Segment.split_and_crop_lines(
            new_segments, console.width, pad=False
        ):
            buffer_extend(line)
        return
    console._buffer.extend(new_segments)

def console_print(
    console: "Console",
    *objects: Any,
    sep: str = " ",
    end: str = "\n",
    style: Optional[Union[str, "Style"]] = None,
    justify: Optional["JustifyMethod"] = None,
    overflow: Optional["OverflowMethod"] = None,
    no_wrap: Optional[bool] = None,
    emoji: Optional[bool] = None,
    markup: Optional[bool] = None,
    highlight: Optional[bool] = None,
    width: Optional[int] = None,
    height: Optional[int] = None,
    crop: bool = True,
    soft_wrap: Optional[bool] = None,
    new_line_start: bool = False,
    no_change: object = None,
    new_line_type: type = None,
) -> None:
    objects = _print_normalize_objects(objects, end, new_line_type)
    no_wrap, overflow, crop = _print_soft_wrap_options(
        console, soft_wrap, no_wrap, overflow, crop
    )
    render_hooks = console._render_hooks[:]
    with console:
        renderables = console._collect_renderables(
            objects,
            sep,
            end,
            justify=justify,
            emoji=emoji,
            markup=markup,
            highlight=highlight,
        )
        for hook in render_hooks:
            renderables = hook.process_renderables(renderables)
        render_options = console.options.update(
            justify=justify,
            overflow=overflow,
            width=min(width, console.width) if width is not None else no_change,
            height=height,
            no_wrap=no_wrap,
            markup=markup,
            highlight=highlight,
        )
        new_segments = _print_collect_segments(
            console, renderables, render_options, style
        )
        if new_line_start:
            _print_apply_new_line_start(new_segments)
        _print_buffer_segments(console, new_segments, crop)