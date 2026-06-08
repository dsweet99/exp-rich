"""Kiss static coverage for rich.markdown."""
import importlib
import io
import logging

def _import_rich(suffix: str):
    return importlib.import_module("rich." + suffix)

# rich.markdown

def test_kiss_markdown_symbols_0():
    _mod = _import_rich('markdown')
    BlockQuote = getattr(_mod, 'BlockQuote')
    CodeBlock = getattr(_mod, 'CodeBlock')
    Heading = getattr(_mod, 'Heading')
    HeadingFormat = getattr(_mod, 'HeadingFormat')
    HorizontalRule = getattr(_mod, 'HorizontalRule')
    ImageItem = getattr(_mod, 'ImageItem')
    Link = getattr(_mod, 'Link')
    ListElement = getattr(_mod, 'ListElement')
    assert BlockQuote is not None
    assert CodeBlock is not None
    assert Heading is not None
    assert HeadingFormat is not None
    assert HorizontalRule is not None
    assert ImageItem is not None
    assert Link is not None
    assert ListElement is not None

def test_kiss_markdown_symbols_1():
    _mod = _import_rich('markdown')
    ListItem = getattr(_mod, 'ListItem')
    Markdown = getattr(_mod, 'Markdown')
    MarkdownContext = getattr(_mod, 'MarkdownContext')
    MarkdownElement = getattr(_mod, 'MarkdownElement')
    Paragraph = getattr(_mod, 'Paragraph')
    TableBodyElement = getattr(_mod, 'TableBodyElement')
    TableDataElement = getattr(_mod, 'TableDataElement')
    TableElement = getattr(_mod, 'TableElement')
    assert ListItem is not None
    assert Markdown is not None
    assert MarkdownContext is not None
    assert MarkdownElement is not None
    assert Paragraph is not None
    assert TableBodyElement is not None
    assert TableDataElement is not None
    assert TableElement is not None

def test_kiss_markdown_symbols_2():
    _mod = _import_rich('markdown')
    TableHeaderElement = getattr(_mod, 'TableHeaderElement')
    TableRowElement = getattr(_mod, 'TableRowElement')
    TextElement = getattr(_mod, 'TextElement')
    UnknownElement = getattr(_mod, 'UnknownElement')
    render_markdown = getattr(_mod, 'render_markdown')
    assert TableHeaderElement is not None
    assert TableRowElement is not None
    assert TextElement is not None
    assert UnknownElement is not None
    assert render_markdown is not None
