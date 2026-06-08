from __future__ import annotations

import sys
from typing import ClassVar, Iterable

from markdown_it import MarkdownIt
from markdown_it.token import Token

from ._markdown_console import markdown_rich_console
from ._markdown_elements import (
    BlockQuote,
    CodeBlock,
    Heading,
    HorizontalRule,
    ImageItem,
    Link,
    ListElement,
    ListItem,
    MarkdownContext,
    MarkdownElement,
    Paragraph,
    TableBodyElement,
    TableDataElement,
    TableElement,
    TableHeaderElement,
    TableRowElement,
    UnknownElement,
)
from .console import Console, ConsoleOptions, JustifyMethod, RenderResult
from ._jupyter_mixin import JupyterMixin
from .style import Style

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
        yield from markdown_rich_console(
            self,
            console,
            options,
            context_type=MarkdownContext,
            link_type=Link,
            unknown_element=UnknownElement,
        )



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

    from rich.console import Console

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