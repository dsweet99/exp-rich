from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import ClassVar, Iterable, get_args

from markdown_it import MarkdownIt
from markdown_it.token import Token

from rich.table import Table

from . import box
from ._loop import loop_first
from ._stack import Stack
from .console import Console, ConsoleOptions, JustifyMethod, RenderResult
from .containers import Renderables
from .rule import Rule
from .segment import Segment
from .style import Style, StyleStack
from .syntax import Syntax
from .text import Text, TextType
from ._jupyter_mixin import JupyterMixin


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


def _markdown_render_exiting(context, console, element, new_line, new_line_segment):
    should_render = not context.stack or (
        context.stack and context.stack.top.on_child_close(context, element)
    )
    if not should_render:
        return
    if new_line:
        yield new_line_segment
    yield from console.render(element, context.options)


def _markdown_render_self_closing(
    context, console, element, token, node_type, new_line, new_line_segment
):
    context.stack.pop()
    text = token.content
    if text is not None:
        element.on_text(context, text)
    should_render = not context.stack or (
        context.stack and context.stack.top.on_child_close(context, element)
    )
    if not should_render:
        return
    if new_line and node_type != "inline":
        yield new_line_segment
    yield from console.render(element, context.options)


def _markdown_render_block_element(
    markdown: "Markdown",
    context: MarkdownContext,
    console: Console,
    token,
    entering: bool,
    exiting: bool,
    self_closing: bool,
    node_type: str,
    new_line: bool,
    new_line_segment: Segment,
) -> Iterable[Segment]:
    element_class = markdown.elements.get(token.type) or UnknownElement
    element = element_class.create(markdown, token)
    if entering or self_closing:
        context.stack.push(element)
        element.on_enter(context)
    if exiting:
        element = context.stack.pop()
        yield from _markdown_render_exiting(context, console, element, new_line, new_line_segment)
        element.on_leave(context)
        return element.new_line
    if self_closing:
        yield from _markdown_render_self_closing(
            context, console, element, token, node_type, new_line, new_line_segment
        )
        element.on_leave(context)
        return element.new_line
    return new_line


def _markdown_yield_text_token(context: MarkdownContext, token) -> bool:
    node_type = token.type
    if node_type == "text":
        context.on_text(token.content, node_type)
        return True
    if node_type == "hardbreak":
        context.on_text("\n", node_type)
        return True
    if node_type == "softbreak":
        context.on_text(" ", node_type)
        return True
    return False


def _markdown_yield_html_inline(
    context: MarkdownContext, console: Console, token
) -> bool:
    if token.type != "html_inline":
        return False
    if token.content == "<kbd>":
        context.enter_style(console.get_style("markdown.kbd", default="bold"))
    elif token.content == "</kbd>":
        context.leave_style()
    return True


def _markdown_yield_tokens(
    markdown: "Markdown", context: MarkdownContext, console: Console
) -> RenderResult:
    new_line = False
    new_line_segment = Segment.line()
    for token in markdown._flatten_tokens(markdown.parsed):
        if _markdown_yield_text_token(context, token):
            continue
        node_type = token.type
        tag = token.tag
        if node_type == "link_open":
            _markdown_handle_link_open(markdown, context, console, token)
            continue
        if _markdown_yield_html_inline(context, console, token):
            continue
        if node_type == "link_close":
            _markdown_handle_link_close(markdown, context, console, token, node_type)
            continue
        if tag in markdown.inlines and node_type not in ("fence", "code_block"):
            _markdown_handle_inline_style(
                context, tag, token.nesting == 1, token.nesting == -1, token
            )
            continue
        new_line = yield from _markdown_render_block_element(
            markdown,
            context,
            console,
            token,
            token.nesting == 1,
            token.nesting == -1,
            token.nesting == 0,
            node_type,
            new_line,
            new_line_segment,
        )


def render_markdown(
    markdown: "Markdown", console: Console, options: ConsoleOptions
) -> RenderResult:
    """Render markdown tokens to the console."""
    style = console.get_style(markdown.style, default="none")
    options = options.update(height=None)
    context = MarkdownContext(
        console,
        options,
        style,
        inline_code_lexer=markdown.inline_code_lexer,
        inline_code_theme=markdown.inline_code_theme,
    )
    yield from _markdown_yield_tokens(markdown, context, console)


def _markdown_handle_link_open(markdown, context, console, token) -> None:
    if markdown.hyperlinks:
        href = str(token.attrs.get("href", ""))
        link_style = console.get_style("markdown.link_url", default="none")
        link_style += Style(link=href)
        context.enter_style(link_style)
    else:
        context.stack.push(Link.create(markdown, token))


def _markdown_handle_link_close(markdown, context, console, token, node_type) -> None:
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


def _markdown_handle_inline_style(context, tag, entering, exiting, token) -> None:
    if entering:
        context.enter_style(f"markdown.{tag}")
        return
    if exiting:
        context.leave_style()
        return
    context.enter_style(f"markdown.{tag}")
    if token.content:
        context.on_text(token.content, token.type)
    context.leave_style()


class Markdown:
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
        yield from render_markdown(self, console, options)

