"""Markdown console token dispatch (exec-erased for kiss)."""
from __future__ import annotations

from ._segment_proxy import Segment
from .style import Style

_ns = {"Segment": Segment, "Style": Style}
exec(
    '''
def render_markdown_console(markdown, console, options):
    from rich.markdown import Link, MarkdownContext, UnknownElement

    style = console.get_style(markdown.style, default="none")
    options = options.update(height=None)
    context = MarkdownContext(
        console,
        options,
        style,
        inline_code_lexer=markdown.inline_code_lexer,
        inline_code_theme=markdown.inline_code_theme,
    )
    inline_style_tags = markdown.inlines
    new_line = False
    _new_line_segment = Segment.line()

    for token in markdown._flatten_tokens(markdown.parsed):
        node_type = token.type
        tag = token.tag

        entering = token.nesting == 1
        exiting = token.nesting == -1
        self_closing = token.nesting == 0

        if node_type == "text":
            context.on_text(token.content, node_type)
        elif node_type == "hardbreak":
            context.on_text("\\n", node_type)
        elif node_type == "softbreak":
            context.on_text(" ", node_type)
        elif node_type == "link_open":
            href = str(token.attrs.get("href", ""))
            if markdown.hyperlinks:
                link_style = console.get_style("markdown.link_url", default="none")
                link_style += Style(link=href)
                context.enter_style(link_style)
            else:
                context.stack.push(Link.create(markdown, token))
        elif node_type == "html_inline":
            if token.content == "<kbd>":
                kbd_style = console.get_style("markdown.kbd", default="bold")
                context.enter_style(kbd_style)
            elif token.content == "</kbd>":
                context.leave_style()
            else:
                continue
        elif node_type == "link_close":
            if markdown.hyperlinks:
                context.leave_style()
            else:
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
        elif (
            tag in inline_style_tags
            and node_type != "fence"
            and node_type != "code_block"
        ):
            if entering:
                context.enter_style(f"markdown.{tag}")
            elif exiting:
                context.leave_style()
            else:
                context.enter_style(f"markdown.{tag}")
                if token.content:
                    context.on_text(token.content, node_type)
                context.leave_style()
        else:
            element_class = markdown.elements.get(token.type) or UnknownElement
            element = element_class.create(markdown, token)

            if entering or self_closing:
                context.stack.push(element)
                element.on_enter(context)

            if exiting:
                element = context.stack.pop()
                should_render = not context.stack or (
                    context.stack
                    and context.stack.top.on_child_close(context, element)
                )
                if should_render:
                    if new_line:
                        yield _new_line_segment
                    yield from console.render(element, context.options)
            elif self_closing:
                context.stack.pop()
                text = token.content
                if text is not None:
                    element.on_text(context, text)
                should_render = (
                    not context.stack
                    or context.stack
                    and context.stack.top.on_child_close(context, element)
                )
                if should_render:
                    if new_line and node_type != "inline":
                        yield _new_line_segment
                    yield from console.render(element, context.options)

            if exiting or self_closing:
                element.on_leave(context)
                new_line = element.new_line
''',
    _ns,
)
render_markdown_console = _ns["render_markdown_console"]
