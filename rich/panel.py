from __future__ import annotations

from ._lazy import import_attr
from typing import TYPE_CHECKING, Optional

AlignMethod = import_attr('rich.align', 'AlignMethod')
ROUNDED = import_attr('rich.box', 'ROUNDED')
Box = import_attr('rich.box', 'Box')
cell_len = import_attr('rich.cells', 'cell_len')
JupyterMixin = import_attr('rich.jupyter', 'JupyterMixin')
Measurement = import_attr('rich.measure', 'Measurement')
measure_renderables = import_attr('rich.measure', 'measure_renderables')
Padding = import_attr('rich.padding', 'Padding')
PaddingDimensions = import_attr('rich.padding', 'PaddingDimensions')
Segment = import_attr('rich.segment', 'Segment')
Style = import_attr('rich.style', 'Style')
StyleType = import_attr('rich.style', 'StyleType')
Text = import_attr('rich.text', 'Text')
TextType = import_attr('rich.text', 'TextType')
if TYPE_CHECKING:
    from .console import Console, ConsoleOptions, RenderableType, RenderResult


def _panel_align_text(
    console: "Console",
    text: Text,
    width: int,
    align: str,
    character: str,
    style: Style,
) -> Text:
    """Gets new aligned text."""
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


def _panel_render_border_text(
    console: "Console",
    border_text: Optional[Text],
    width: int,
    align: str,
    box: Box,
    border_style: Style,
    child_options: "ConsoleOptions",
    *,
    top: bool,
) -> "RenderResult":
    if border_text is None or width <= 4:
        edge = box.get_top([width - 2]) if top else box.get_bottom([width - 2])
        yield Segment(edge, border_style)
        return
    border_text.stylize_before(border_style)
    border_text = _panel_align_text(
        console,
        border_text,
        width - 4,
        align,
        box.top if top else box.bottom,
        border_style,
    )
    left = box.top_left if top else box.bottom_left
    right = box.top_right if top else box.bottom_right
    edge_char = box.top if top else box.bottom
    yield Segment(left + edge_char, border_style)
    yield from console.render(border_text, child_options.update_width(width - 4))
    yield Segment(edge_char + right, border_style)


def _panel_child_dimensions(
    console: "Console",
    renderable: "RenderableType",
    options: "ConsoleOptions",
    *,
    width: int,
    expand: bool,
    height: Optional[int],
    title_text: Optional[Text],
) -> tuple[int, Optional[int]]:
    child_width = (
        width - 2
        if expand
        else console.measure(
            renderable, options=options.update_width(width - 2)
        ).maximum
    )
    child_height = height or options.height or None
    if child_height:
        child_height -= 2
    if title_text is not None:
        child_width = min(
            options.max_width - 2, max(child_width, title_text.cell_len + 2)
        )
    return child_width + 2, child_height


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
        box: Box = ROUNDED,
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
        box: Box = ROUNDED,
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
    def _title(self) -> Optional[Text]:
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
    def _subtitle(self) -> Optional[Text]:
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
        _padding = Padding.unpack(self.padding)
        renderable = (
            Padding(self.renderable, _padding) if any(_padding) else self.renderable
        )
        style = console.get_style(self.style)
        border_style = style + console.get_style(self.border_style)
        width = (
            options.max_width
            if self.width is None
            else min(options.max_width, self.width)
        )

        safe_box: bool = console.safe_box if self.safe_box is None else self.safe_box
        box = self.box.substitute(options, safe=safe_box)

        title_text = self._title
        width, child_height = _panel_child_dimensions(
            console,
            renderable,
            options,
            width=width,
            expand=self.expand,
            height=self.height,
            title_text=title_text,
        )
        child_width = width - 2
        child_options = options.update(
            width=child_width, height=child_height, highlight=self.highlight
        )
        lines = console.render_lines(renderable, child_options, style=style)

        line_start = Segment(box.mid_left, border_style)
        line_end = Segment(f"{box.mid_right}", border_style)
        new_line = Segment.line()
        yield from _panel_render_border_text(
            console,
            title_text,
            width,
            self.title_align,
            box,
            border_style,
            child_options,
            top=True,
        )

        yield new_line
        for line in lines:
            yield line_start
            yield from line
            yield line_end
            yield new_line

        yield from _panel_render_border_text(
            console,
            self._subtitle,
            width,
            self.subtitle_align,
            box,
            border_style,
            child_options,
            top=False,
        )
        yield new_line

    def __rich_measure__(
        self, console: "Console", options: "ConsoleOptions"
    ) -> "Measurement":
        _title = self._title
        _, right, _, left = Padding.unpack(self.padding)
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
    Console = import_attr('rich.console', 'Console')

    c = Console()

    DOUBLE = import_attr('rich.box', 'DOUBLE')
    ROUNDED = import_attr('rich.box', 'ROUNDED')
    Padding = import_attr('rich.padding', 'Padding')

    p = Panel(
        "Hello, World!",
        title="rich.Panel",
        style="white on blue",
        box=DOUBLE,
        padding=1,
    )

    c.print()
    c.print(p)
