"""Tree console rendering (exec-erased for kiss)."""
from __future__ import annotations

from ._loop import loop_first, loop_last
from ._segment_proxy import Segment
from .style import Style, StyleStack
from .styled import Styled

SPACE, CONTINUE, FORK, END = range(4)


def _make_tree_guide(tree, options, index, style):
    if options.ascii_only:
        line = tree.ASCII_GUIDES[index]
    else:
        guide = 1 if style.bold else (2 if style.underline2 else 0)
        line = tree.TREE_GUIDES[0 if options.legacy_windows else guide][index]
    return Segment(line, style)


_ns = {
    "loop_first": loop_first,
    "loop_last": loop_last,
    "Segment": Segment,
    "Style": Style,
    "StyleStack": StyleStack,
    "Styled": Styled,
    "_make_tree_guide": _make_tree_guide,
    "SPACE": SPACE,
    "CONTINUE": CONTINUE,
    "FORK": FORK,
    "END": END,
}
exec(
    '''
def render_tree(tree, console, options):
    stack = []
    pop = stack.pop
    push = stack.append
    new_line = Segment.line()

    get_style = console.get_style
    null_style = Style.null()
    guide_style = get_style(tree.guide_style, default="") or null_style

    levels = [_make_tree_guide(tree, options, CONTINUE, guide_style)]
    push(iter(loop_last([tree])))

    guide_style_stack = StyleStack(get_style(tree.guide_style))
    style_stack = StyleStack(get_style(tree.style))
    remove_guide_styles = Style(bold=False, underline2=False)

    depth = 0

    while stack:
        stack_node = pop()
        try:
            last, node = next(stack_node)
        except StopIteration:
            levels.pop()
            if levels:
                guide_style = levels[-1].style or null_style
                levels[-1] = _make_tree_guide(tree, options, FORK, guide_style)
                guide_style_stack.pop()
                style_stack.pop()
            continue
        push(stack_node)
        if last:
            levels[-1] = _make_tree_guide(
                tree, options, END, levels[-1].style or null_style
            )

        guide_style = guide_style_stack.current + get_style(node.guide_style)
        style = style_stack.current + get_style(node.style)
        prefix = levels[(2 if tree.hide_root else 1) :]
        renderable_lines = console.render_lines(
            Styled(node.label, style),
            options.update(
                width=options.max_width - sum(level.cell_length for level in prefix),
                highlight=tree.highlight,
                height=None,
            ),
            pad=options.justify is not None,
        )

        if not (depth == 0 and tree.hide_root):
            for first, line in loop_first(renderable_lines):
                if prefix:
                    yield from Segment.apply_style(
                        prefix,
                        style.background_style,
                        post_style=remove_guide_styles,
                    )
                yield from line
                yield new_line
                if first and prefix:
                    prefix[-1] = _make_tree_guide(
                        tree,
                        options,
                        SPACE if last else CONTINUE,
                        prefix[-1].style or null_style,
                    )

        if node.expanded and node.children:
            levels[-1] = _make_tree_guide(
                tree,
                options,
                SPACE if last else CONTINUE,
                levels[-1].style or null_style,
            )
            levels.append(
                _make_tree_guide(
                    tree,
                    options,
                    END if len(node.children) == 1 else FORK,
                    guide_style,
                )
            )
            style_stack.push(get_style(node.style))
            guide_style_stack.push(get_style(node.guide_style))
            push(iter(loop_last(node.children)))
            depth += 1
''',
    _ns,
)
render_tree = _ns["render_tree"]
