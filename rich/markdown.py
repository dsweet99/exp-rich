from __future__ import annotations
from ._lazy import import_attr, import_submodule

import sys
from dataclasses import dataclass
from typing import ClassVar, Iterable, List, get_args

from markdown_it import MarkdownIt
from markdown_it.token import Token

Table = import_attr('rich.table', 'Table')

box = import_submodule('rich.box')
loop_first = import_attr('rich._loop', 'loop_first')
Stack = import_attr('rich._stack', 'Stack')
Console = import_attr('rich.console', 'Console')
ConsoleOptions = import_attr('rich.console', 'ConsoleOptions')
JustifyMethod = import_attr('rich.console', 'JustifyMethod')
RenderResult = import_attr('rich.console', 'RenderResult')
Renderables = import_attr('rich.containers', 'Renderables')
JupyterMixin = import_attr('rich.jupyter', 'JupyterMixin')
Rule = import_attr('rich.rule', 'Rule')
Segment = import_attr('rich.segment', 'Segment')
Style = import_attr('rich.style', 'Style')
StyleStack = import_attr('rich.style', 'StyleStack')
Syntax = import_attr('rich.syntax', 'Syntax')
Text = import_attr('rich.text', 'Text')
TextType = import_attr('rich.text', 'TextType')


class MarkdownElement:
    new_line: ClassVar[bool] = True

    @classmethod
    def create(cls, markdown: Markdown, token: Token) -> MarkdownElement:
        """Factory to create markdown element,

        Args:
            markdown (Markdown): The parent Markdown object.
            token (Token): A node from markdown-it.

        Returns:
            MarkdownElement: A new markdown element
        """
        return cls()

    def on_enter(self, context: MarkdownContext) -> None:
        """Called when the node is entered.

        Args:
            context (MarkdownContext): The markdown context.
        """

    def on_text(self, context: MarkdownContext, text: TextType) -> None:
        """Called when text is parsed.

        Args:
            context (MarkdownContext): The markdown context.
        """

    def on_leave(self, context: MarkdownContext) -> None:
        """Called when the parser leaves the element.

        Args:
            context (MarkdownContext): [description]
        """

    def on_child_close(self, context: MarkdownContext, child: MarkdownElement) -> bool:
        """Called when a child element is closed.

        This method allows a parent element to take over rendering of its children.

        Args:
            context (MarkdownContext): The markdown context.
            child (MarkdownElement): The child markdown element.

        Returns:
            bool: Return True to render the element, or False to not render the element.
        """
        return True

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        return ()


class UnknownElement(MarkdownElement):
    """An unknown element.

    Hopefully there will be no unknown elements, and we will have a MarkdownElement for
    everything in the document.

    """


class TextElement(MarkdownElement):
    """Base class for elements that render text."""

    style_name = "none"

    def on_enter(self, context: MarkdownContext) -> None:
        self.style = context.enter_style(self.style_name)
        self.text = Text(justify="left")

    def on_text(self, context: MarkdownContext, text: TextType) -> None:
        self.text.append(text, context.current_style if isinstance(text, str) else None)

    def on_leave(self, context: MarkdownContext) -> None:
        context.leave_style()


class Paragraph(TextElement):
    """A Paragraph."""

    style_name = "markdown.paragraph"
    justify: JustifyMethod

    @classmethod
    def create(cls, markdown: Markdown, token: Token) -> Paragraph:
        return cls(justify=markdown.justify or "left")

    def __init__(self, justify: JustifyMethod) -> None:
        self.justify = justify

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        self.text.justify = self.justify
        yield self.text


@dataclass
class HeadingFormat:
    justify: JustifyMethod = "left"
    style: str = ""


class Heading(TextElement):
    """A heading."""

    LEVEL_ALIGN: ClassVar[dict[str, JustifyMethod]] = {
        "h1": "center",
        "h2": "left",
        "h3": "left",
        "h4": "left",
        "h5": "left",
        "h6": "left",
    }

    @classmethod
    def create(cls, markdown: Markdown, token: Token) -> Heading:
        return cls(token.tag)

    def on_enter(self, context: MarkdownContext) -> None:
        self.text = Text()
        context.enter_style(self.style_name)

    def __init__(self, tag: str) -> None:
        self.tag = tag
        self.style_name = f"markdown.{tag}"
        super().__init__()

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        text = self.text.copy()
        heading_justify = self.LEVEL_ALIGN.get(self.tag, "left")
        text.justify = heading_justify
        yield text


class CodeBlock(TextElement):
    """A code block with syntax highlighting."""

    style_name = "markdown.code_block"

    @classmethod
    def create(cls, markdown: Markdown, token: Token) -> CodeBlock:
        node_info = token.info or ""
        lexer_name = node_info.partition(" ")[0]
        return cls(lexer_name or "text", markdown.code_theme)

    def __init__(self, lexer_name: str, theme: str) -> None:
        self.lexer_name = lexer_name
        self.theme = theme

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        code = str(self.text).rstrip()
        syntax = Syntax(
            code, self.lexer_name, theme=self.theme, word_wrap=True, padding=1
        )
        yield syntax


class BlockQuote(TextElement):
    """A block quote."""

    style_name = "markdown.block_quote"

    def __init__(self) -> None:
        self.elements: Renderables = Renderables()

    def on_child_close(self, context: MarkdownContext, child: MarkdownElement) -> bool:
        self.elements.append(child)
        return False

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        render_options = options.update(width=options.max_width - 4)
        lines = console.render_lines(self.elements, render_options, style=self.style)
        style = self.style
        new_line = Segment("\n")
        padding = Segment("▌ ", style)
        for line in lines:
            yield padding
            yield from line
            yield new_line


class HorizontalRule(MarkdownElement):
    """A horizontal rule to divide sections."""

    new_line = False

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        style = console.get_style("markdown.hr", default="none")
        yield Rule(style=style, characters="-")
        yield Text()


class TableElement(MarkdownElement):
    """MarkdownElement corresponding to `table_open`."""

    def __init__(self) -> None:
        self.header: TableHeaderElement | None = None
        self.body: TableBodyElement | None = None

    def on_child_close(self, context: MarkdownContext, child: MarkdownElement) -> bool:
        if isinstance(child, TableHeaderElement):
            self.header = child
        elif isinstance(child, TableBodyElement):
            self.body = child
        else:
            raise RuntimeError("Couldn't process markdown table.")
        return False

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        table = Table(
            box=box.SIMPLE,
            pad_edge=False,
            style="markdown.table.border",
            show_edge=True,
            collapse_padding=True,
        )

        if self.header is not None and self.header.row is not None:
            for column in self.header.row.cells:
                heading = column.content.copy()
                heading.stylize("markdown.table.header")
                table.add_column(heading)

        if self.body is not None:
            for row in self.body.rows:
                row_content = [element.content for element in row.cells]
                table.add_row(*row_content)

        yield table


class TableHeaderElement(MarkdownElement):
    """MarkdownElement corresponding to `thead_open` and `thead_close`."""

    def __init__(self) -> None:
        self.row: TableRowElement | None = None

    def on_child_close(self, context: MarkdownContext, child: MarkdownElement) -> bool:
        assert isinstance(child, TableRowElement)
        self.row = child
        return False


class TableBodyElement(MarkdownElement):
    """MarkdownElement corresponding to `tbody_open` and `tbody_close`."""

    def __init__(self) -> None:
        self.rows: list[TableRowElement] = []

    def on_child_close(self, context: MarkdownContext, child: MarkdownElement) -> bool:
        assert isinstance(child, TableRowElement)
        self.rows.append(child)
        return False


class TableRowElement(MarkdownElement):
    """MarkdownElement corresponding to `tr_open` and `tr_close`."""

    def __init__(self) -> None:
        self.cells: list[TableDataElement] = []

    def on_child_close(self, context: MarkdownContext, child: MarkdownElement) -> bool:
        assert isinstance(child, TableDataElement)
        self.cells.append(child)
        return False


class TableDataElement(MarkdownElement):
    """MarkdownElement corresponding to `td_open` and `td_close`
    and `th_open` and `th_close`."""

    @classmethod
    def create(cls, markdown: Markdown, token: Token) -> MarkdownElement:
        style = str(token.attrs.get("style")) or ""

        justify: JustifyMethod
        if "text-align:right" in style:
            justify = "right"
        elif "text-align:center" in style:
            justify = "center"
        elif "text-align:left" in style:
            justify = "left"
        else:
            justify = "default"

        assert justify in get_args(JustifyMethod)
        return cls(justify=justify)

    def __init__(self, justify: JustifyMethod) -> None:
        self.content: Text = Text("", justify=justify)
        self.justify = justify

    def on_text(self, context: MarkdownContext, text: TextType) -> None:
        if isinstance(text, str):
            self.content.append(text, context.current_style)
        else:
            self.content.append_text(text)


class ListElement(MarkdownElement):
    """A list element."""

    @classmethod
    def create(cls, markdown: Markdown, token: Token) -> ListElement:
        return cls(token.type, int(token.attrs.get("start", 1)))

    def __init__(self, list_type: str, list_start: int | None) -> None:
        self.items: list[ListItem] = []
        self.list_type = list_type
        self.list_start = list_start

    def on_child_close(self, context: MarkdownContext, child: MarkdownElement) -> bool:
        assert isinstance(child, ListItem)
        self.items.append(child)
        return False

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        if self.list_type == "bullet_list_open":
            for item in self.items:
                yield from item.render_bullet(console, options)
        else:
            number = 1 if self.list_start is None else self.list_start
            last_number = number + len(self.items)
            for index, item in enumerate(self.items):
                yield from item.render_number(
                    console, options, number + index, last_number
                )


class ListItem(TextElement):
    """An item in a list."""

    style_name = "markdown.item"

    def __init__(self) -> None:
        self.elements: Renderables = Renderables()

    def on_child_close(self, context: MarkdownContext, child: MarkdownElement) -> bool:
        self.elements.append(child)
        return False

    def render_bullet(self, console: Console, options: ConsoleOptions) -> RenderResult:
        render_options = options.update(width=options.max_width - 3)
        lines = console.render_lines(self.elements, render_options, style=self.style)
        bullet_style = console.get_style("markdown.item.bullet", default="none")

        bullet = Segment(" • ", bullet_style)
        padding = Segment(" " * 3, bullet_style)
        new_line = Segment("\n")
        for first, line in loop_first(lines):
            yield bullet if first else padding
            yield from line
            yield new_line

    def render_number(
        self, console: Console, options: ConsoleOptions, number: int, last_number: int
    ) -> RenderResult:
        number_width = len(str(last_number)) + 2
        render_options = options.update(width=options.max_width - number_width)
        lines = console.render_lines(self.elements, render_options, style=self.style)
        number_style = console.get_style("markdown.item.number", default="none")

        new_line = Segment("\n")
        padding = Segment(" " * number_width, number_style)
        numeral = Segment(f"{number}".rjust(number_width - 1) + " ", number_style)
        for first, line in loop_first(lines):
            yield numeral if first else padding
            yield from line
            yield new_line


class Link(TextElement):
    @classmethod
    def create(cls, markdown: Markdown, token: Token) -> MarkdownElement:
        url = token.attrs.get("href", "#")
        return cls(token.content, str(url))

    def __init__(self, text: str, href: str):
        self.text = Text(text)
        self.href = href


class ImageItem(TextElement):
    """Renders a placeholder for an image."""

    new_line = False

    @classmethod
    def create(cls, markdown: Markdown, token: Token) -> MarkdownElement:
        """Factory to create markdown element,

        Args:
            markdown (Markdown): The parent Markdown object.
            token (Any): A token from markdown-it.

        Returns:
            MarkdownElement: A new markdown element
        """
        return cls(str(token.attrs.get("src", "")), markdown.hyperlinks)

    def __init__(self, destination: str, hyperlinks: bool) -> None:
        self.destination = destination
        self.hyperlinks = hyperlinks
        self.link: str | None = None
        super().__init__()

    def on_enter(self, context: MarkdownContext) -> None:
        self.link = context.current_style.link
        self.text = Text(justify="left")
        super().on_enter(context)

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        link_style = Style(link=self.link or self.destination or None)
        title = self.text or Text(self.destination.strip("/").rsplit("/", 1)[-1])
        if self.hyperlinks:
            title.stylize(link_style)
        text = Text.assemble("🌆 ", title, " ", end="")
        yield text


class MarkdownContext:
    """Manages the console render state."""

    def __init__(
        self,
        console: Console,
        options: ConsoleOptions,
        style: Style,
        inline_code_lexer: str | None = None,
        inline_code_theme: str = "monokai",
    ) -> None:
        self.console = console
        self.options = options
        self.style_stack: StyleStack = StyleStack(style)
        self.stack: Stack[MarkdownElement] = Stack()

        self._syntax: Syntax | None = None
        if inline_code_lexer is not None:
            self._syntax = Syntax("", inline_code_lexer, theme=inline_code_theme)

    @property
    def current_style(self) -> Style:
        """Current style which is the product of all styles on the stack."""
        return self.style_stack.current

    def on_text(self, text: str, node_type: str) -> None:
        """Called when the parser visits text."""
        if node_type in {"fence", "code_inline"} and self._syntax is not None:
            highlight_text = self._syntax.highlight(text)
            highlight_text.rstrip()
            self.stack.top.on_text(
                self, Text.assemble(highlight_text, style=self.style_stack.current)
            )
        else:
            self.stack.top.on_text(self, text)

    def enter_style(self, style_name: str | Style) -> Style:
        """Enter a style context."""
        style = self.console.get_style(style_name, default="none")
        self.style_stack.push(style)
        return self.current_style

    def leave_style(self) -> Style:
        """Leave a style context."""
        style = self.style_stack.pop()
        return style


def _markdown_apply_text_token(
    context: "MarkdownContext", token: Token, node_type: str
) -> None:
    if node_type == "text":
        context.on_text(token.content, node_type)
    elif node_type == "hardbreak":
        context.on_text("\n", node_type)
    elif node_type == "softbreak":
        context.on_text(" ", node_type)


def _markdown_apply_link_open(
    markdown: "Markdown",
    context: "MarkdownContext",
    console: Console,
    token: Token,
) -> None:
    href = str(token.attrs.get("href", ""))
    if markdown.hyperlinks:
        link_style = console.get_style("markdown.link_url", default="none")
        link_style += Style(link=href)
        context.enter_style(link_style)
        return
    context.stack.push(Link.create(markdown, token))


def _markdown_apply_html_inline(
    context: "MarkdownContext", console: Console, token: Token
) -> bool:
    if token.content == "<kbd>":
        context.enter_style(console.get_style("markdown.kbd", default="bold"))
        return True
    if token.content == "</kbd>":
        context.leave_style()
        return True
    return False


def _markdown_apply_link_close(
    markdown: "Markdown",
    context: "MarkdownContext",
    console: Console,
    token: Token,
    node_type: str,
) -> None:
    if markdown.hyperlinks:
        context.leave_style()
        return
    element = context.stack.pop()
    assert isinstance(element, Link)
    link_style = console.get_style("markdown.link", default="none")
    context.enter_style(link_style)
    context.on_text(element.text.plain, node_type)
    context.leave_style()
    context.on_text(" (", node_type)
    link_url_style = console.get_style("markdown.link_url", default="none")
    context.enter_style(link_url_style)
    context.on_text(element.href, node_type)
    context.leave_style()
    context.on_text(")", node_type)


def _markdown_apply_inline_style(
    context: "MarkdownContext",
    token: Token,
    tag: str,
    *,
    entering: bool,
    exiting: bool,
    self_closing: bool,
    node_type: str,
) -> None:
    if entering:
        context.enter_style(f"markdown.{tag}")
        return
    if exiting:
        context.leave_style()
        return
    context.enter_style(f"markdown.{tag}")
    if token.content:
        context.on_text(token.content, node_type)
    context.leave_style()


def _markdown_collect_exiting_segments(
    context: "MarkdownContext",
    console: Console,
    *,
    new_line: bool,
    new_line_segment: Segment,
) -> tuple[List[Segment], bool]:
    element = context.stack.pop()
    should_render = not context.stack or (
        context.stack and context.stack.top.on_child_close(context, element)
    )
    segments: List[Segment] = []
    if should_render:
        if new_line:
            segments.append(new_line_segment)
        segments.extend(console.render(element, context.options))
    element.on_leave(context)
    return segments, element.new_line


def _markdown_collect_self_closing_segments(
    context: "MarkdownContext",
    console: Console,
    element: MarkdownElement,
    token: Token,
    *,
    node_type: str,
    new_line: bool,
    new_line_segment: Segment,
) -> tuple[List[Segment], bool]:
    context.stack.pop()
    text = token.content
    if text is not None:
        element.on_text(context, text)
    should_render = not context.stack or (
        context.stack and context.stack.top.on_child_close(context, element)
    )
    if not should_render:
        element.on_leave(context)
        return [], element.new_line
    segments: List[Segment] = []
    if new_line and node_type != "inline":
        segments.append(new_line_segment)
    segments.extend(console.render(element, context.options))
    element.on_leave(context)
    return segments, element.new_line


def _markdown_render_block_element(
    markdown: "Markdown",
    context: "MarkdownContext",
    console: Console,
    token: Token,
    *,
    node_type: str,
    entering: bool,
    exiting: bool,
    self_closing: bool,
    new_line: bool,
    new_line_segment: Segment,
) -> tuple[bool, RenderResult]:
    element_class = markdown.elements.get(token.type) or UnknownElement
    element = element_class.create(markdown, token)

    if entering or self_closing:
        context.stack.push(element)
        element.on_enter(context)

    segments_to_yield: List[Segment] = []
    updated_new_line = new_line
    if exiting:
        segments_to_yield, updated_new_line = _markdown_collect_exiting_segments(
            context, console, new_line=new_line, new_line_segment=new_line_segment
        )
    elif self_closing:
        segments_to_yield, updated_new_line = _markdown_collect_self_closing_segments(
            context,
            console,
            element,
            token,
            node_type=node_type,
            new_line=new_line,
            new_line_segment=new_line_segment,
        )

    def _gen() -> RenderResult:
        yield from segments_to_yield

    return updated_new_line, _gen()


def _markdown_dispatch_token(
    markdown: "Markdown",
    context: "MarkdownContext",
    console: Console,
    token: Token,
    *,
    inline_style_tags: set[str],
    new_line: bool,
    new_line_segment: Segment,
) -> tuple[bool, RenderResult]:
    node_type = token.type
    tag = token.tag
    entering = token.nesting == 1
    exiting = token.nesting == -1
    self_closing = token.nesting == 0

    if node_type in {"text", "hardbreak", "softbreak"}:
        _markdown_apply_text_token(context, token, node_type)
        return new_line, ()
    if node_type == "link_open":
        _markdown_apply_link_open(markdown, context, console, token)
        return new_line, ()
    if node_type == "html_inline":
        if _markdown_apply_html_inline(context, console, token):
            return new_line, ()
        return new_line, ()
    if node_type == "link_close":
        _markdown_apply_link_close(markdown, context, console, token, node_type)
        return new_line, ()
    if tag in inline_style_tags and node_type not in {"fence", "code_block"}:
        _markdown_apply_inline_style(
            context,
            token,
            tag,
            entering=entering,
            exiting=exiting,
            self_closing=self_closing,
            node_type=node_type,
        )
        return new_line, ()

    updated_new_line, block_output = _markdown_render_block_element(
        markdown,
        context,
        console,
        token,
        node_type=node_type,
        entering=entering,
        exiting=exiting,
        self_closing=self_closing,
        new_line=new_line,
        new_line_segment=new_line_segment,
    )
    return updated_new_line, block_output


class Markdown(JupyterMixin):
    """A Markdown renderable.

    Args:
        markup (str): A string containing markdown.
        code_theme (str, optional): Pygments theme for code blocks. Defaults to "monokai". See https://pygments.org/styles/ for code themes.
        justify (JustifyMethod, optional): Justify value for paragraphs. Defaults to None.
        style (Union[str, Style], optional): Optional style to apply to markdown.
        hyperlinks (bool, optional): Enable hyperlinks. Defaults to ``True``.
        inline_code_lexer: (str, optional): Lexer to use if inline code highlighting is
            enabled. Defaults to None.
        inline_code_theme: (Optional[str], optional): Pygments theme for inline code
            highlighting, or None for no highlighting. Defaults to None.
    """

    elements: ClassVar[dict[str, type[MarkdownElement]]] = {
        "paragraph_open": Paragraph,
        "heading_open": Heading,
        "fence": CodeBlock,
        "code_block": CodeBlock,
        "blockquote_open": BlockQuote,
        "hr": HorizontalRule,
        "bullet_list_open": ListElement,
        "ordered_list_open": ListElement,
        "list_item_open": ListItem,
        "image": ImageItem,
        "table_open": TableElement,
        "tbody_open": TableBodyElement,
        "thead_open": TableHeaderElement,
        "tr_open": TableRowElement,
        "td_open": TableDataElement,
        "th_open": TableDataElement,
    }

    inlines = {"em", "strong", "code", "s"}

    def __init__(
        self,
        markup: str,
        code_theme: str = "monokai",
        justify: JustifyMethod | None = None,
        style: str | Style = "none",
        hyperlinks: bool = True,
        inline_code_lexer: str | None = None,
        inline_code_theme: str | None = None,
    ) -> None:
        parser = MarkdownIt().enable("strikethrough").enable("table")
        self.markup = markup
        self.parsed = parser.parse(markup)
        self.code_theme = code_theme
        self.justify: JustifyMethod | None = justify
        self.style = style
        self.hyperlinks = hyperlinks
        self.inline_code_lexer = inline_code_lexer
        self.inline_code_theme = inline_code_theme or code_theme

    def _flatten_tokens(self, tokens: Iterable[Token]) -> Iterable[Token]:
        """Flattens the token stream."""
        for token in tokens:
            is_fence = token.type == "fence"
            is_image = token.tag == "img"
            if token.children and not (is_image or is_fence):
                yield from self._flatten_tokens(token.children)
            else:
                yield token

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        """Render markdown to the console."""
        style = console.get_style(self.style, default="none")
        options = options.update(height=None)
        context = MarkdownContext(
            console,
            options,
            style,
            inline_code_lexer=self.inline_code_lexer,
            inline_code_theme=self.inline_code_theme,
        )
        tokens = self.parsed
        inline_style_tags = self.inlines
        new_line = False
        _new_line_segment = Segment.line()

        for token in self._flatten_tokens(tokens):
            new_line, output = _markdown_dispatch_token(
                self,
                context,
                console,
                token,
                inline_style_tags=inline_style_tags,
                new_line=new_line,
                new_line_segment=_new_line_segment,
            )
            yield from output


if __name__ == "__main__":  # pragma: no cover
    import argparse
    import sys

    parser = argparse.ArgumentParser(
        description="Render Markdown to the console with Rich"
    )
    parser.add_argument(
        "path",
        metavar="PATH",
        help="path to markdown file, or - for stdin",
    )
    parser.add_argument(
        "-c",
        "--force-color",
        dest="force_color",
        action="store_true",
        default=None,
        help="force color for non-terminals",
    )
    parser.add_argument(
        "-t",
        "--code-theme",
        dest="code_theme",
        default="monokai",
        help="pygments code theme",
    )
    parser.add_argument(
        "-i",
        "--inline-code-lexer",
        dest="inline_code_lexer",
        default=None,
        help="inline_code_lexer",
    )
    parser.add_argument(
        "-y",
        "--hyperlinks",
        dest="hyperlinks",
        action="store_true",
        help="enable hyperlinks",
    )
    parser.add_argument(
        "-w",
        "--width",
        type=int,
        dest="width",
        default=None,
        help="width of output (default will auto-detect)",
    )
    parser.add_argument(
        "-j",
        "--justify",
        dest="justify",
        action="store_true",
        help="enable full text justify",
    )
    parser.add_argument(
        "-p",
        "--page",
        dest="page",
        action="store_true",
        help="use pager to scroll output",
    )
    args = parser.parse_args()

    Console = import_attr('rich.console', 'Console')

    if args.path == "-":
        markdown_body = sys.stdin.read()
    else:
        with open(args.path, encoding="utf-8") as markdown_file:
            markdown_body = markdown_file.read()

    markdown = Markdown(
        markdown_body,
        justify="full" if args.justify else "left",
        code_theme=args.code_theme,
        hyperlinks=args.hyperlinks,
        inline_code_lexer=args.inline_code_lexer,
    )
    if args.page:
        import io
        import pydoc

        fileio = io.StringIO()
        console = Console(
            file=fileio, force_terminal=args.force_color, width=args.width
        )
        console.print(markdown)
        pydoc.pager(fileio.getvalue())

    else:
        console = Console(
            force_terminal=args.force_color, width=args.width, record=True
        )
        console.print(markdown)
