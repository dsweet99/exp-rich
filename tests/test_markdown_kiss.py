"""Behavioral unit tests for rich.markdown element methods."""

import io

from markdown_it.token import Token

from rich.console import Console
from rich.markdown import (
    BlockQuote,
    CodeBlock,
    Heading,
    ImageItem,
    Link,
    ListElement,
    ListItem,
    Markdown,
    MarkdownContext,
    MarkdownElement,
    Paragraph,
    TableBodyElement,
    TableDataElement,
    TableElement,
    TableHeaderElement,
    TableRowElement,
    TextElement,
    UnknownElement,
)
from rich.style import Style


def _render(renderable) -> str:
    console = Console(file=io.StringIO(), width=80, legacy_windows=False)
    console.print(renderable)
    return console.file.getvalue()


def _make_context(
    *, inline_code_lexer: str | None = None, inline_code_theme: str = "monokai"
) -> MarkdownContext:
    console = Console(file=io.StringIO(), width=80)
    return MarkdownContext(
        console,
        console.options,
        Style(),
        inline_code_lexer=inline_code_lexer,
        inline_code_theme=inline_code_theme,
    )


def _token(
    type_: str,
    tag: str = "",
    *,
    nesting: int = 1,
    attrs: dict | None = None,
    content: str = "",
    info: str = "",
) -> Token:
    token = Token(type_, tag, nesting)
    token.attrs = attrs or {}
    token.content = content
    token.info = info
    return token


def test_markdown_element_base_lifecycle():
    element = UnknownElement()
    context = _make_context()
    md = Markdown("hello")

    created = MarkdownElement.create(md, _token("unknown"))
    assert isinstance(created, MarkdownElement)

    element.on_enter(context)
    element.on_text(context, "plain")
    element.on_leave(context)
    assert element.on_child_close(context, UnknownElement()) is True


def test_text_element_lifecycle():
    element = TextElement()
    context = _make_context()

    element.on_enter(context)
    element.on_text(context, "styled text")
    element.on_leave(context)

    assert element.text.plain == "styled text"


def test_paragraph_create_and_render():
    md = Markdown("centered", justify="center")
    paragraph = Paragraph.create(md, _token("paragraph_open"))
    assert paragraph.justify == "center"

    context = _make_context()
    paragraph.on_enter(context)
    paragraph.on_text(context, "Hello")
    paragraph.on_leave(context)

    assert "Hello" in _render(paragraph)


def test_heading_create_and_style():
    md = Markdown("# Title")
    heading = Heading.create(md, _token("heading_open", "h1"))
    context = _make_context()

    heading.on_enter(context)
    heading.on_text(context, "Title")
    heading.on_leave(context)

    assert heading.tag == "h1"
    assert heading.text.plain == "Title"


def test_code_block_create_renders_syntax():
    md = Markdown("```python\nprint(1)\n```")
    block = CodeBlock.create(md, _token("fence", info="python"))
    context = _make_context()

    block.on_enter(context)
    block.on_text(context, "print(1)")
    block.on_leave(context)

    assert "print" in _render(block)


def test_block_quote_collects_children():
    quote = BlockQuote()
    child = Paragraph(justify="left")
    context = _make_context()

    assert quote.on_child_close(context, child) is False
    assert list(quote.elements) == [child]

    child.on_enter(context)
    child.on_text(context, "quoted")
    child.on_leave(context)
    quote.on_enter(context)
    rendered = _render(quote)
    assert "▌" in rendered
    assert "quoted" in rendered


def test_table_elements_assemble_rows():
    table = TableElement()
    header = TableHeaderElement()
    body = TableBodyElement()
    row = TableRowElement()
    cell = TableDataElement(justify="left")
    context = _make_context()

    cell.on_text(context, "cell")
    assert table.on_child_close(context, header) is False
    assert table.on_child_close(context, body) is False
    assert header.on_child_close(context, row) is False
    assert body.on_child_close(context, row) is False
    assert row.on_child_close(context, cell) is False

    table.header = header
    table.header.row = row
    row.cells = [cell]
    table.body = body
    table.body.rows = [row]

    assert "cell" in _render(table)


def test_table_data_create_respects_alignment():
    md = Markdown("| a |")
    right = TableDataElement.create(
        md, _token("td_open", attrs={"style": "text-align:right"})
    )
    center = TableDataElement.create(
        md, _token("td_open", attrs={"style": "text-align:center"})
    )
    assert right.justify == "right"
    assert center.justify == "center"


def test_list_element_and_items():
    md = Markdown("- one\n- two")
    bullet_list = ListElement.create(md, _token("bullet_list_open"))
    ordered = ListElement.create(
        md, _token("ordered_list_open", attrs={"start": 3})
    )
    item = ListItem()
    child = Paragraph(justify="left")
    context = _make_context()

    assert bullet_list.on_child_close(context, item) is False
    item.on_child_close(context, child) is False
    item.on_enter(context)
    child.on_enter(context)
    child.on_text(context, "item text")
    child.on_leave(context)
    bullet_list.items = [item]
    ordered.items = [item]

    assert "•" in _render(bullet_list)

    console = Console(file=io.StringIO(), width=40)
    number_lines = list(item.render_number(console, console.options, 3, 9))
    assert number_lines


def test_link_create_stores_href():
    md = Markdown("[x](http://example.com)")
    link = Link.create(md, _token("link_open", attrs={"href": "http://example.com"}))
    assert link.href == "http://example.com"


def test_image_item_create_and_enter():
    md = Markdown("![alt](img.png)", hyperlinks=True)
    image = ImageItem.create(
        md, _token("image", attrs={"src": "https://example.com/img.png"})
    )
    context = _make_context()
    image.on_enter(context)
    image.on_text(context, "alt")

    assert "🌆" in _render(image)


def test_markdown_context_style_stack():
    context = _make_context(inline_code_lexer="python")
    element = TextElement()
    context.stack.push(element)
    element.on_enter(context)

    entered = context.enter_style("bold")
    assert context.current_style == entered

    context.on_text("plain", "text")
    context.on_text("x = 1", "code_inline")

    element.on_leave(context)
    left = context.leave_style()
    assert left is not None


def test_markdown_render_exercises_parser_hooks():
    md = Markdown(
        "# H\n\n> quote\n\n- a\n\n1. b\n\n[link](http://x.com)\n\n![i](u)\n\n---\n\n|h|\n|-|\n|v|",
        justify="left",
    )
    rendered = _render(md)
    assert "H" in rendered
    assert "quote" in rendered
    assert "link" in rendered
