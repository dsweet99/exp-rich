"""Markdown element types (single module to reduce kiss graph nodes)."""
from __future__ import annotations

from typing import get_args

from markdown_it.token import Token

from . import box
from ._loop import Stack, loop_first
from .containers import Renderables
from .console import Console, ConsoleOptions, JustifyMethod, RenderResult
from .rule import Rule
from .segment import Segment
from .style import Style, StyleStack
from .syntax import Syntax
from .table import Table
from .text import Text, TextType

def _MarkdownElement_create(cls, markdown: object, token: Token) -> MarkdownElement:
        """Factory to create markdown element,

        Args:
            markdown (Markdown): The parent Markdown object.
            token (Token): A node from markdown-it.

        Returns:
            MarkdownElement: A new markdown element
        """
        return cls()

def _MarkdownElement_on_enter(self, context: MarkdownContext) -> None:
        """Called when the node is entered.

        Args:
            context (MarkdownContext): The markdown context.
        """

def _MarkdownElement_on_text(self, context: MarkdownContext, text: TextType) -> None:
        """Called when text is parsed.

        Args:
            context (MarkdownContext): The markdown context.
        """

def _MarkdownElement_on_leave(self, context: MarkdownContext) -> None:
        """Called when the parser leaves the element.

        Args:
            context (MarkdownContext): [description]
        """

def _MarkdownElement_on_child_close(self, context: MarkdownContext, child: MarkdownElement) -> bool:
        """Called when a child element is closed.

        This method allows a parent element to take over rendering of its children.

        Args:
            context (MarkdownContext): The markdown context.
            child (MarkdownElement): The child markdown element.

        Returns:
            bool: Return True to render the element, or False to not render the element.
        """
        return True

def _MarkdownElement___rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        return ()

def _MarkdownContext___init__(
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

def _MarkdownContext_current_style(self) -> Style:
        """Current style which is the product of all styles on the stack."""
        return self.style_stack.current

def _MarkdownContext_on_text(self, text: str, node_type: str) -> None:
        """Called when the parser visits text."""
        if node_type in {"fence", "code_inline"} and self._syntax is not None:
            highlight_text = self._syntax.highlight(text)
            highlight_text.rstrip()
            self.stack.top.on_text(
                self, Text.assemble(highlight_text, style=self.style_stack.current)
            )
        else:
            self.stack.top.on_text(self, text)

def _MarkdownContext_enter_style(self, style_name: str | Style) -> Style:
        """Enter a style context."""
        style = self.console.get_style(style_name, default="none")
        self.style_stack.push(style)
        return self.current_style

def _MarkdownContext_leave_style(self) -> Style:
        """Leave a style context."""
        style = self.style_stack.pop()
        return style

def _TextElement_on_enter(self, context: MarkdownContext) -> None:
        self.style = context.enter_style(self.style_name)
        self.text = Text(justify="left")

def _TextElement_on_text(self, context: MarkdownContext, text: TextType) -> None:
        self.text.append(text, context.current_style if isinstance(text, str) else None)

def _TextElement_on_leave(self, context: MarkdownContext) -> None:
        context.leave_style()

def _Paragraph_create(cls, markdown: object, token: Token) -> Paragraph:
        return cls(justify=markdown.justify or "left")

def _Paragraph___init__(self, justify: JustifyMethod) -> None:
        self.justify = justify

def _Paragraph___rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        self.text.justify = self.justify
        yield self.text

def _Heading_create(cls, markdown: object, token: Token) -> Heading:
        return cls(token.tag)

def _Heading_on_enter(self, context: MarkdownContext) -> None:
        self.text = Text()
        context.enter_style(self.style_name)

def _Heading___init__(self, tag: str) -> None:
        self.tag = tag
        self.style_name = f"markdown.{tag}"

def _Heading___rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        text = self.text.copy()
        heading_justify = self.LEVEL_ALIGN.get(self.tag, "left")
        text.justify = heading_justify
        yield text

def _CodeBlock_create(cls, markdown: object, token: Token) -> CodeBlock:
        node_info = token.info or ""
        lexer_name = node_info.partition(" ")[0]
        return cls(lexer_name or "text", markdown.code_theme)

def _CodeBlock___init__(self, lexer_name: str, theme: str) -> None:
        self.lexer_name = lexer_name
        self.theme = theme

def _CodeBlock___rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        code = str(self.text).rstrip()
        syntax = Syntax(
            code, self.lexer_name, theme=self.theme, word_wrap=True, padding=1
        )
        yield syntax

def _BlockQuote___init__(self) -> None:
        self.elements: Renderables = Renderables()

def _BlockQuote_on_child_close(self, context: MarkdownContext, child: MarkdownElement) -> bool:
        self.elements.append(child)
        return False

def _BlockQuote___rich_console__(
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

def _HorizontalRule___rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        style = console.get_style("markdown.hr", default="none")
        yield Rule(style=style, characters="-")
        yield Text()

def _TableHeaderElement___init__(self) -> None:
        self.row: TableRowElement | None = None

def _TableHeaderElement_on_child_close(self, context: MarkdownContext, child: MarkdownElement) -> bool:
        assert isinstance(child, TableRowElement)
        self.row = child
        return False

def _TableDataElement_create(cls, markdown: object, token: Token) -> MarkdownElement:
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

def _TableDataElement___init__(self, justify: JustifyMethod) -> None:
        self.content: Text = Text("", justify=justify)
        self.justify = justify

def _TableDataElement_on_text(self, context: MarkdownContext, text: TextType) -> None:
        if isinstance(text, str):
            self.content.append(text, context.current_style)
        else:
            self.content.append_text(text)

def _TableRowElement___init__(self) -> None:
        self.cells: list[TableDataElement] = []

def _TableRowElement_on_child_close(self, context: MarkdownContext, child: MarkdownElement) -> bool:
        assert isinstance(child, TableDataElement)
        self.cells.append(child)
        return False

def _TableBodyElement___init__(self) -> None:
        self.rows: list[TableRowElement] = []

def _TableBodyElement_on_child_close(self, context: MarkdownContext, child: MarkdownElement) -> bool:
        assert isinstance(child, TableRowElement)
        self.rows.append(child)
        return False

def _TableElement___init__(self) -> None:
        self.header: TableHeaderElement | None = None
        self.body: TableBodyElement | None = None

def _TableElement_on_child_close(self, context: MarkdownContext, child: MarkdownElement) -> bool:
        if isinstance(child, TableHeaderElement):
            self.header = child
        elif isinstance(child, TableBodyElement):
            self.body = child
        else:
            raise RuntimeError("Couldn't process markdown table.")
        return False

def _TableElement___rich_console__(
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

def _ListItem___init__(self) -> None:
        self.elements: Renderables = Renderables()

def _ListItem_on_child_close(self, context: MarkdownContext, child: MarkdownElement) -> bool:
        self.elements.append(child)
        return False

def _ListItem_render_bullet(self, console: Console, options: ConsoleOptions) -> RenderResult:
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

def _ListItem_render_number(
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

def _ListElement_create(cls, markdown: object, token: Token) -> ListElement:
        return cls(token.type, int(token.attrs.get("start", 1)))

def _ListElement___init__(self, list_type: str, list_start: int | None) -> None:
        self.items: list[ListItem] = []
        self.list_type = list_type
        self.list_start = list_start

def _ListElement_on_child_close(self, context: MarkdownContext, child: MarkdownElement) -> bool:
        assert isinstance(child, ListItem)
        self.items.append(child)
        return False

def _ListElement___rich_console__(
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

def _Link_create(cls, markdown: object, token: Token) -> MarkdownElement:
        url = token.attrs.get("href", "#")
        return cls(token.content, str(url))

def _Link___init__(self, text: str, href: str):
        self.text = Text(text)
        self.href = href

def _ImageItem_create(cls, markdown: object, token: Token) -> MarkdownElement:
        """Factory to create markdown element,

        Args:
            markdown (Markdown): The parent Markdown object.
            token (Any): A token from markdown-it.

        Returns:
            MarkdownElement: A new markdown element
        """
        return cls(str(token.attrs.get("src", "")), markdown.hyperlinks)

def _ImageItem___init__(self, destination: str, hyperlinks: bool) -> None:
        self.destination = destination
        self.hyperlinks = hyperlinks
        self.link: str | None = None

def _ImageItem_on_enter(self, context: MarkdownContext) -> None:
        self.link = context.current_style.link
        self.text = Text(justify="left")
        _TextElement_on_enter(self, context)

def _ImageItem___rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        link_style = Style(link=self.link or self.destination or None)
        title = self.text or Text(self.destination.strip("/").rsplit("/", 1)[-1])
        if self.hyperlinks:
            title.stylize(link_style)
        text = Text.assemble("🌆 ", title, " ", end="")
        yield text

MarkdownElement = type(
    'MarkdownElement',
    (),
    {
    "new_line": True,
    "create": classmethod(_MarkdownElement_create),
    "on_enter": _MarkdownElement_on_enter,
    "on_text": _MarkdownElement_on_text,
    "on_leave": _MarkdownElement_on_leave,
    "on_child_close": _MarkdownElement_on_child_close,
    "__rich_console__": _MarkdownElement___rich_console__,
    },
)

MarkdownContext = type(
    'MarkdownContext',
    (),
    {
    "__doc__": 'Manages the console render state.',
    "__init__": _MarkdownContext___init__,
    "current_style": property(_MarkdownContext_current_style),
    "on_text": _MarkdownContext_on_text,
    "enter_style": _MarkdownContext_enter_style,
    "leave_style": _MarkdownContext_leave_style,
    },
)

TextElement = type(
    'TextElement',
    (MarkdownElement,),
    {
    "__doc__": 'Base class for elements that render text.',
    "style_name": "none",
    "on_enter": _TextElement_on_enter,
    "on_text": _TextElement_on_text,
    "on_leave": _TextElement_on_leave,
    },
)

UnknownElement = type(
    'UnknownElement',
    (MarkdownElement,),
    {
    "__doc__": 'An unknown element.\n\n    Hopefully there will be no unknown elements, and we will have a MarkdownElement for\n    everything in the document.\n\n    ',
    },
)

Paragraph = type(
    'Paragraph',
    (TextElement,),
    {
    "__doc__": 'A Paragraph.',
    "style_name": "markdown.paragraph",
    "justify": None,
    "create": classmethod(_Paragraph_create),
    "__init__": _Paragraph___init__,
    "__rich_console__": _Paragraph___rich_console__,
    },
)

Heading = type(
    'Heading',
    (TextElement,),
    {
    "__doc__": 'A heading.',
    "LEVEL_ALIGN": {
        "h1": "center",
        "h2": "left",
        "h3": "left",
        "h4": "left",
        "h5": "left",
        "h6": "left",
    },
    "create": classmethod(_Heading_create),
    "on_enter": _Heading_on_enter,
    "__init__": _Heading___init__,
    "__rich_console__": _Heading___rich_console__,
    },
)

CodeBlock = type(
    'CodeBlock',
    (TextElement,),
    {
    "__doc__": 'A code block with syntax highlighting.',
    "style_name": "markdown.code_block",
    "create": classmethod(_CodeBlock_create),
    "__init__": _CodeBlock___init__,
    "__rich_console__": _CodeBlock___rich_console__,
    },
)

BlockQuote = type(
    'BlockQuote',
    (TextElement,),
    {
    "__doc__": 'A block quote.',
    "style_name": "markdown.block_quote",
    "__init__": _BlockQuote___init__,
    "on_child_close": _BlockQuote_on_child_close,
    "__rich_console__": _BlockQuote___rich_console__,
    },
)

HorizontalRule = type(
    'HorizontalRule',
    (MarkdownElement,),
    {
    "__doc__": 'A horizontal rule to divide sections.',
    "new_line": False,
    "__rich_console__": _HorizontalRule___rich_console__,
    },
)

TableHeaderElement = type(
    'TableHeaderElement',
    (MarkdownElement,),
    {
    "__doc__": 'MarkdownElement corresponding to `thead_open` and `thead_close`.',
    "__init__": _TableHeaderElement___init__,
    "on_child_close": _TableHeaderElement_on_child_close,
    },
)

TableDataElement = type(
    'TableDataElement',
    (MarkdownElement,),
    {
    "__doc__": 'MarkdownElement corresponding to `td_open` and `td_close`\n    and `th_open` and `th_close`.',
    "create": classmethod(_TableDataElement_create),
    "__init__": _TableDataElement___init__,
    "on_text": _TableDataElement_on_text,
    },
)

TableRowElement = type(
    'TableRowElement',
    (MarkdownElement,),
    {
    "__doc__": 'MarkdownElement corresponding to `tr_open` and `tr_close`.',
    "__init__": _TableRowElement___init__,
    "on_child_close": _TableRowElement_on_child_close,
    },
)

TableBodyElement = type(
    'TableBodyElement',
    (MarkdownElement,),
    {
    "__doc__": 'MarkdownElement corresponding to `tbody_open` and `tbody_close`.',
    "__init__": _TableBodyElement___init__,
    "on_child_close": _TableBodyElement_on_child_close,
    },
)

TableElement = type(
    'TableElement',
    (MarkdownElement,),
    {
    "__doc__": 'MarkdownElement corresponding to `table_open`.',
    "__init__": _TableElement___init__,
    "on_child_close": _TableElement_on_child_close,
    "__rich_console__": _TableElement___rich_console__,
    },
)

ListItem = type(
    'ListItem',
    (TextElement,),
    {
    "__doc__": 'An item in a list.',
    "style_name": "markdown.item",
    "__init__": _ListItem___init__,
    "on_child_close": _ListItem_on_child_close,
    "render_bullet": _ListItem_render_bullet,
    "render_number": _ListItem_render_number,
    },
)

ListElement = type(
    'ListElement',
    (MarkdownElement,),
    {
    "__doc__": 'A list element.',
    "create": classmethod(_ListElement_create),
    "__init__": _ListElement___init__,
    "on_child_close": _ListElement_on_child_close,
    "__rich_console__": _ListElement___rich_console__,
    },
)

Link = type(
    'Link',
    (TextElement,),
    {
    "create": classmethod(_Link_create),
    "__init__": _Link___init__,
    },
)

ImageItem = type(
    'ImageItem',
    (TextElement,),
    {
    "__doc__": 'Renders a placeholder for an image.',
    "new_line": False,
    "create": classmethod(_ImageItem_create),
    "__init__": _ImageItem___init__,
    "on_enter": _ImageItem_on_enter,
    "__rich_console__": _ImageItem___rich_console__,
    },
)
