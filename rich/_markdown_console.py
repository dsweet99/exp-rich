from typing import Any, Iterable, Type

from .segment import Segment
from .style import Style


def _markdown_handle_link_open(
    markdown: Any, console: Any, context: Any, token: Any, link_type: Type
) -> None:
    href = str(token.attrs.get("href", ""))
    if markdown.hyperlinks:
        link_style = console.get_style("markdown.link_url", default="none")
        link_style += Style(link=href)
        context.enter_style(link_style)
    else:
        context.stack.push(link_type.create(markdown, token))


def _markdown_handle_link_close(
    markdown: Any, console: Any, context: Any, token: Any, link_type: Type
) -> None:
    if markdown.hyperlinks:
        context.leave_style()
        return
    element = context.stack.pop()
    assert isinstance(element, link_type)
    link_style = console.get_style("markdown.link", default="none")
    context.enter_style(link_style)
    context.on_text(element.text.plain, token.type)
    context.leave_style()
    context.on_text(" (", token.type)
    link_url_style = console.get_style("markdown.link_url", default="none")
    context.enter_style(link_url_style)
    context.on_text(element.href, token.type)
    context.leave_style()
    context.on_text(")", token.type)


def _markdown_handle_inline_style(
    context: Any, token: Any, tag: str, inline_style_tags: set, node_type: str
) -> None:
    if tag not in inline_style_tags or node_type in ("fence", "code_block"):
        return
    entering = token.nesting == 1
    exiting = token.nesting == -1
    if entering:
        context.enter_style(f"markdown.{tag}")
    elif exiting:
        context.leave_style()
    else:
        context.enter_style(f"markdown.{tag}")
        if token.content:
            context.on_text(token.content, node_type)
        context.leave_style()


def _markdown_should_render(context: Any, element: Any) -> bool:
    return not context.stack or (
        context.stack and context.stack.top.on_child_close(context, element)
    )


def _markdown_render_exiting(
    console: Any,
    context: Any,
    element: Any,
    new_line_state: list,
    new_line_segment: Segment,
) -> Iterable[Any]:
    if not _markdown_should_render(context, element):
        return
    if new_line_state[0]:
        yield new_line_segment
    yield from console.render(element, context.options)


def _markdown_render_self_closing(
    console: Any,
    context: Any,
    element: Any,
    token: Any,
    node_type: str,
    new_line_state: list,
    new_line_segment: Segment,
) -> Iterable[Any]:
    text = token.content
    if text is not None:
        element.on_text(context, text)
    if not _markdown_should_render(context, element):
        return
    if new_line_state[0] and node_type != "inline":
        yield new_line_segment
    yield from console.render(element, context.options)


def _markdown_render_element(
    markdown: Any,
    console: Any,
    context: Any,
    token: Any,
    *,
    unknown_element: Type,
    new_line_state: list,
    new_line_segment: Segment,
) -> Iterable[Any]:
    element_class = markdown.elements.get(token.type) or unknown_element
    element = element_class.create(markdown, token)
    entering = token.nesting == 1
    exiting = token.nesting == -1
    self_closing = token.nesting == 0
    node_type = token.type

    if entering or self_closing:
        context.stack.push(element)
        element.on_enter(context)

    if exiting:
        element = context.stack.pop()
        yield from _markdown_render_exiting(
            console, context, element, new_line_state, new_line_segment
        )
    elif self_closing:
        context.stack.pop()
        yield from _markdown_render_self_closing(
            console,
            context,
            element,
            token,
            node_type,
            new_line_state,
            new_line_segment,
        )

    if exiting or self_closing:
        element.on_leave(context)
        new_line_state[0] = element.new_line


def _markdown_dispatch_token(
    markdown: Any,
    console: Any,
    context: Any,
    token: Any,
    *,
    link_type: Type,
    unknown_element: Type,
    inline_style_tags: set,
    new_line_state: list,
    new_line_segment: Segment,
) -> Iterable[Any]:
    node_type = token.type
    tag = token.tag

    if node_type == "text":
        context.on_text(token.content, node_type)
        return
    if node_type == "hardbreak":
        context.on_text("\n", node_type)
        return
    if node_type == "softbreak":
        context.on_text(" ", node_type)
        return
    if node_type in {"link_open", "link_close"}:
        if node_type == "link_open":
            _markdown_handle_link_open(markdown, console, context, token, link_type)
        else:
            _markdown_handle_link_close(markdown, console, context, token, link_type)
        return
    if node_type == "html_inline":
        if token.content == "<kbd>":
            context.enter_style(console.get_style("markdown.kbd", default="bold"))
        elif token.content == "</kbd>":
            context.leave_style()
        return
    if tag in inline_style_tags and node_type not in ("fence", "code_block"):
        _markdown_handle_inline_style(
            context, token, tag, inline_style_tags, node_type
        )
        return
    yield from _markdown_render_element(
        markdown,
        console,
        context,
        token,
        unknown_element=unknown_element,
        new_line_state=new_line_state,
        new_line_segment=new_line_segment,
    )


def markdown_rich_console(
    markdown: Any,
    console: Any,
    options: Any,
    *,
    context_type: Type,
    link_type: Type,
    unknown_element: Type,
) -> Iterable[Any]:
    """Render markdown tokens to the console."""
    style = console.get_style(markdown.style, default="none")
    options = options.update(height=None)
    context = context_type(
        console,
        options,
        style,
        inline_code_lexer=markdown.inline_code_lexer,
        inline_code_theme=markdown.inline_code_theme,
    )
    inline_style_tags = markdown.inlines
    new_line_state = [False]
    new_line_segment = Segment.line()

    for token in markdown._flatten_tokens(markdown.parsed):
        yield from _markdown_dispatch_token(
            markdown,
            console,
            context,
            token,
            link_type=link_type,
            unknown_element=unknown_element,
            inline_style_tags=inline_style_tags,
            new_line_state=new_line_state,
            new_line_segment=new_line_segment,
        )
