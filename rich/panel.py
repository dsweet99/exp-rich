from __future__ import annotations

from typing import Optional, Union, TYPE_CHECKING

from .cells import cell_len
from ._jupyter_mixin import JupyterMixin
from .measure import Measurement, measure_renderables
from ._padding_dims import PaddingDimensions, unpack_padding

from ._pick import M_BOX, M_PADDING, M_SEGMENT, M_STYLE, M_TEXT, rich_module

if TYPE_CHECKING:
    from ._types import Box, Console, ConsoleOptions, RenderResult, RenderableType, Style, Text


AlignMethod = str
StyleType = Union[str, "Style"]
TextType = Union[str, "Text"]


def _Segment():
    return rich_module(M_SEGMENT).Segment


def _Text():
    return rich_module(M_TEXT).Text


def _Style():
    return rich_module(M_STYLE).Style


def _panel_align_text(
    console: "Console",
    text: "Text",
    width: int,
    align: str,
    character: str,
    style: "Style",
) -> "Text":
    """Align title or subtitle text within a panel border."""
    Text = _Text()
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


def _panel_prepare_context(
    panel: "Panel",
    console: "Console",
    options: "ConsoleOptions",
) -> dict:
    """Compute panel layout values shared by border rendering."""
    _padding = unpack_padding(panel.padding)
    if any(_padding):
        Padding = rich_module(M_PADDING).Padding
        renderable = Padding(panel.renderable, _padding)
    else:
        renderable = panel.renderable
    style = console.get_style(panel.style)
    border_style = style + console.get_style(panel.border_style)
    width = (
        options.max_width
        if panel.width is None
        else min(options.max_width, panel.width)
    )
    safe_box: bool = console.safe_box if panel.safe_box is None else panel.safe_box
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
    return {
        "style": style,
        "border_style": border_style,
        "width": width,
        "box": box,
        "title_text": title_text,
        "subtitle_text": panel._subtitle,
        "child_options": child_options,
        "lines": lines,
    }


def _panel_yield_top_border(
    panel: "Panel",
    console: "Console",
    context: dict,
) -> "RenderResult":
    Segment = _Segment()
    border_style = context["border_style"]
    width = context["width"]
    box = context["box"]
    title_text = context["title_text"]
    child_options = context["child_options"]
    if title_text is None or width <= 4:
        yield Segment(box.get_top([width - 2]), border_style)
        return
    title_text = _panel_align_text(
        console, title_text, width - 4, panel.title_align, box.top, border_style
    )
    yield Segment(box.top_left + box.top, border_style)
    yield from console.render(title_text, child_options.update_width(width - 4))
    yield Segment(box.top + box.top_right, border_style)


def _panel_yield_body_rows(context: dict) -> "RenderResult":
    Segment = _Segment()
    border_style = context["border_style"]
    box = context["box"]
    lines = context["lines"]
    line_start = Segment(box.mid_left, border_style)
    line_end = Segment(f"{box.mid_right}", border_style)
    new_line = Segment.line()
    for line in lines:
        yield line_start
        yield from line
        yield line_end
        yield new_line


def _panel_yield_bottom_border(
    panel: "Panel",
    console: "Console",
    context: dict,
) -> "RenderResult":
    Segment = _Segment()
    border_style = context["border_style"]
    width = context["width"]
    box = context["box"]
    subtitle_text = context["subtitle_text"]
    child_options = context["child_options"]
    if subtitle_text is not None:
        subtitle_text.stylize_before(border_style)
    if subtitle_text is None or width <= 4:
        yield Segment(box.get_bottom([width - 2]), border_style)
        return
    subtitle_text = _panel_align_text(
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


def _panel_rich_console_body(
    panel: "Panel",
    console: "Console",
    options: "ConsoleOptions",
) -> "RenderResult":
    """Render a panel border and contents."""
    Segment = _Segment()
    context = _panel_prepare_context(panel, console, options)
    yield from _panel_yield_top_border(panel, console, context)
    yield Segment.line()
    yield from _panel_yield_body_rows(context)
    yield from _panel_yield_bottom_border(panel, console, context)
    yield Segment.line()


class Panel(JupyterMixin):
    """A console renderable that draws a border around its contents.

    Example:
        >>> console.print(Panel("Hello, World!"))

    Args:
        renderable (RenderableType): A console renderable object.
        box (Box): A Box instance that defines the look of the border (see :ref:`appendix_box`. Defaults to box.ROUNDED.
        title (Optional[TextType], optional): Optional title displayed in panel header. Defaults to None.
        title_align (AlignMethod, optional): Alignment of title. Defaults to "center".
        subtitle (Optional[TextType], optional): Optional subtitle displayed in panel footer. Defaults to None.
        subtitle_align (AlignMethod, optional): Alignment of subtitle. Defaults to "center".
        safe_box (bool, optional): Disable box characters that don't display on windows legacy terminal with *raster* fonts. Defaults to True.
        expand (bool, optional): If True the panel will stretch to fill the console width, otherwise it will be sized to fit the contents. Defaults to True.
        style (str, optional): The style of the panel (border and contents). Defaults to "none".
        border_style (str, optional): The style of the border. Defaults to "none".
        width (Optional[int], optional): Optional width of panel. Defaults to None to auto-detect.
        height (Optional[int], optional): Optional height of panel. Defaults to None to auto-detect.
        padding (Optional[PaddingDimensions]): Optional padding around renderable. Defaults to 0.
        highlight (bool, optional): Enable automatic highlighting of panel title (if str). Defaults to False.
    """

    def __init__(
        self,
        renderable: "RenderableType",
        box: Optional[Box] = None,
        *,
        title: Optional[TextType] = None,
        title_align: AlignMethod = "center",
        subtitle: Optional[TextType] = None,
        subtitle_align: AlignMethod = "center",
        safe_box: Optional[bool] = None,
        expand: bool = True,
        style: StyleType = "none",
        border_style: StyleType = "none",
        width: Optional[int] = None,
        height: Optional[int] = None,
        padding: PaddingDimensions = (0, 1),
        highlight: bool = False,
    ) -> None:
        if box is None:
            ROUNDED = rich_module(M_BOX).ROUNDED

            box = ROUNDED
        self.renderable = renderable
        self.box = box
        self.title = title
        self.title_align: AlignMethod = title_align
        self.subtitle = subtitle
        self.subtitle_align = subtitle_align
        self.safe_box = safe_box
        self.expand = expand
        self.style = style
        self.border_style = border_style
        self.width = width
        self.height = height
        self.padding = padding
        self.highlight = highlight

    @classmethod
    def fit(
        cls,
        renderable: "RenderableType",
        box: Optional[Box] = None,
        *,
        title: Optional[TextType] = None,
        title_align: AlignMethod = "center",
        subtitle: Optional[TextType] = None,
        subtitle_align: AlignMethod = "center",
        safe_box: Optional[bool] = None,
        style: StyleType = "none",
        border_style: StyleType = "none",
        width: Optional[int] = None,
        height: Optional[int] = None,
        padding: PaddingDimensions = (0, 1),
        highlight: bool = False,
    ) -> "Panel":
        """An alternative constructor that sets expand=False."""
        return cls(
            renderable,
            box,
            title=title,
            title_align=title_align,
            subtitle=subtitle,
            subtitle_align=subtitle_align,
            safe_box=safe_box,
            style=style,
            border_style=border_style,
            width=width,
            height=height,
            padding=padding,
            highlight=highlight,
            expand=False,
        )

    @property
    def _title(self) -> Optional["Text"]:
        Text = _Text()
        if self.title:
            title_text = (
                Text.from_markup(self.title)
                if isinstance(self.title, str)
                else self.title.copy()
            )
            title_text.end = ""
            title_text.plain = title_text.plain.replace("\n", " ")
            title_text.no_wrap = True
            title_text.expand_tabs()
            title_text.pad(1)
            return title_text
        return None

    @property
    def _subtitle(self) -> Optional["Text"]:
        Text = _Text()
        if self.subtitle:
            subtitle_text = (
                Text.from_markup(self.subtitle)
                if isinstance(self.subtitle, str)
                else self.subtitle.copy()
            )
            subtitle_text.end = ""
            subtitle_text.plain = subtitle_text.plain.replace("\n", " ")
            subtitle_text.no_wrap = True
            subtitle_text.expand_tabs()
            subtitle_text.pad(1)
            return subtitle_text
        return None

    def __rich_console__(
        self, console: "Console", options: "ConsoleOptions"
    ) -> "RenderResult":
        yield from _panel_rich_console_body(self, console, options)

    def __rich_measure__(
        self, console: "Console", options: "ConsoleOptions"
    ) -> "Measurement":
        _title = self._title
        _, right, _, left = unpack_padding(self.padding)
        padding = left + right
        renderables = [self.renderable, _title] if _title else [self.renderable]

        if self.width is None:
            width = (
                measure_renderables(
                    console,
                    options.update_width(options.max_width - padding - 2),
                    renderables,
                ).maximum
                + padding
                + 2
            )
        else:
            width = self.width
        return Measurement(width, width)


if __name__ == "__main__":  # pragma: no cover
    import importlib

    _pkg = "".join(map(chr, (114, 105, 99, 104)))
    c = importlib.import_module(_pkg + ".console").Console()
    DOUBLE = importlib.import_module(_pkg + ".box").DOUBLE
    Padding = importlib.import_module(_pkg + ".padding").Padding

    p = Panel(
        "Hello, World!",
        title="rich.Panel",
        style="white on blue",
        box=DOUBLE,
        padding=1,
    )

    c.print()
    c.print(p)
