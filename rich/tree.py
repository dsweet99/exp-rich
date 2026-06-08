from __future__ import annotations

from typing import Iterator, List, Optional, Tuple

from ._loop import loop_first, loop_last
from .console import Console, ConsoleOptions, RenderableType, RenderResult
from ._jupyter_mixin import JupyterMixin
from .measure import Measurement
from .segment import Segment
from .style import Style, StyleStack, StyleType
from .styled import Styled

GuideType = Tuple[str, str, str, str]

SPACE, CONTINUE, FORK, END = range(4)


def _make_tree_guide(
    tree: "Tree", options: "ConsoleOptions", index: int, style: Style
) -> Segment:
    if options.ascii_only:
        line = tree.ASCII_GUIDES[index]
    else:
        guide = 1 if style.bold else (2 if style.underline2 else 0)
        line = tree.TREE_GUIDES[0 if options.legacy_windows else guide][index]
    return Segment(line, style)


def _yield_tree_node_lines(
    tree: "Tree",
    console: "Console",
    options: "ConsoleOptions",
    node: "Tree",
    style: Style,
    prefix: List[Segment],
    last: bool,
    make_guide,
    new_line: Segment,
    remove_guide_styles: Style,
) -> "RenderResult":
    renderable_lines = console.render_lines(
        Styled(node.label, style),
        options.update(
            width=options.max_width - sum(level.cell_length for level in prefix),
            highlight=tree.highlight,
            height=None,
        ),
        pad=options.justify is not None,
    )
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
            prefix[-1] = make_guide(
                SPACE if last else CONTINUE, prefix[-1].style or Style.null()
            )


def _tree_unwind_level(
    levels: List[Segment],
    guide_style_stack: StyleStack,
    style_stack: StyleStack,
    make_guide,
    null_style: Style,
) -> None:
    levels.pop()
    if not levels:
        return
    guide_style = levels[-1].style or null_style
    levels[-1] = make_guide(FORK, guide_style)
    guide_style_stack.pop()
    style_stack.pop()


def _tree_push_children(
    stack: List[Iterator[Tuple[bool, "Tree"]]],
    push,
    levels: List[Segment],
    style_stack: StyleStack,
    guide_style_stack: StyleStack,
    get_style,
    node: "Tree",
    last: bool,
    guide_style: Style,
    make_guide,
) -> None:
    levels[-1] = make_guide(
        SPACE if last else CONTINUE, levels[-1].style or Style.null()
    )
    levels.append(make_guide(END if len(node.children) == 1 else FORK, guide_style))
    style_stack.push(get_style(node.style))
    guide_style_stack.push(get_style(node.guide_style))
    push(iter(loop_last(node.children)))


def _tree_visit_node(
    tree: "Tree",
    console: "Console",
    options: "ConsoleOptions",
    stack: List[Iterator[Tuple[bool, "Tree"]]],
    pop,
    push,
    levels: List[Segment],
    guide_style_stack: StyleStack,
    style_stack: StyleStack,
    get_style,
    make_guide,
    new_line: Segment,
    remove_guide_styles: Style,
    null_style: Style,
    depth: int,
    last: bool,
    node: "Tree",
) -> "RenderResult":
    if last:
        levels[-1] = make_guide(END, levels[-1].style or null_style)

    node_guide_style = guide_style_stack.current + get_style(node.guide_style)
    style = style_stack.current + get_style(node.style)
    prefix = levels[(2 if tree.hide_root else 1) :]

    if not (depth == 0 and tree.hide_root):
        yield from _yield_tree_node_lines(
            tree,
            console,
            options,
            node,
            style,
            prefix,
            last,
            make_guide,
            new_line,
            remove_guide_styles,
        )

    if node.expanded and node.children:
        _tree_push_children(
            stack,
            push,
            levels,
            style_stack,
            guide_style_stack,
            get_style,
            node,
            last,
            node_guide_style,
            make_guide,
        )
        return depth + 1
    return depth


def _render_tree_segments(
    tree: "Tree", console: "Console", options: "ConsoleOptions"
) -> "RenderResult":
    stack: List[Iterator[Tuple[bool, Tree]]] = []
    pop = stack.pop
    push = stack.append
    new_line = Segment.line()
    get_style = console.get_style
    null_style = Style.null()
    guide_style = get_style(tree.guide_style, default="") or null_style
    def make_guide(index, style):
        return _make_tree_guide(tree, options, index, style)

    levels: List[Segment] = [make_guide(CONTINUE, guide_style)]
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
            _tree_unwind_level(levels, guide_style_stack, style_stack, make_guide, null_style)
            continue
        push(stack_node)
        depth = yield from _tree_visit_node(
            tree,
            console,
            options,
            stack,
            pop,
            push,
            levels,
            guide_style_stack,
            style_stack,
            get_style,
            make_guide,
            new_line,
            remove_guide_styles,
            null_style,
            depth,
            last,
            node,
        )


class Tree(JupyterMixin):
    """A renderable for a tree structure.

    Attributes:
        ASCII_GUIDES (GuideType): Guide lines used when Console.ascii_only is True.
        TREE_GUIDES (List[GuideType, GuideType, GuideType]): Default guide lines.

    Args:
        label (RenderableType): The renderable or str for the tree label.
        style (StyleType, optional): Style of this tree. Defaults to "tree".
        guide_style (StyleType, optional): Style of the guide lines. Defaults to "tree.line".
        expanded (bool, optional): Also display children. Defaults to True.
        highlight (bool, optional): Highlight renderable (if str). Defaults to False.
        hide_root (bool, optional): Hide the root node. Defaults to False.
    """

    ASCII_GUIDES = ("    ", "|   ", "+-- ", "`-- ")
    TREE_GUIDES = [
        ("    ", "│   ", "├── ", "└── "),
        ("    ", "┃   ", "┣━━ ", "┗━━ "),
        ("    ", "║   ", "╠══ ", "╚══ "),
    ]

    def __init__(
        self,
        label: RenderableType,
        *,
        style: StyleType = "tree",
        guide_style: StyleType = "tree.line",
        expanded: bool = True,
        highlight: bool = False,
        hide_root: bool = False,
    ) -> None:
        self.label = label
        self.style = style
        self.guide_style = guide_style
        self.children: List[Tree] = []
        self.expanded = expanded
        self.highlight = highlight
        self.hide_root = hide_root

    def add(
        self,
        label: RenderableType,
        *,
        style: Optional[StyleType] = None,
        guide_style: Optional[StyleType] = None,
        expanded: bool = True,
        highlight: Optional[bool] = False,
    ) -> "Tree":
        """Add a child tree.

        Args:
            label (RenderableType): The renderable or str for the tree label.
            style (StyleType, optional): Style of this tree. Defaults to "tree".
            guide_style (StyleType, optional): Style of the guide lines. Defaults to "tree.line".
            expanded (bool, optional): Also display children. Defaults to True.
            highlight (Optional[bool], optional): Highlight renderable (if str). Defaults to False.

        Returns:
            Tree: A new child Tree, which may be further modified.
        """
        node = Tree(
            label,
            style=self.style if style is None else style,
            guide_style=self.guide_style if guide_style is None else guide_style,
            expanded=expanded,
            highlight=self.highlight if highlight is None else highlight,
        )
        self.children.append(node)
        return node

    def __rich_console__(
        self, console: "Console", options: "ConsoleOptions"
    ) -> "RenderResult":
        yield from _render_tree_segments(self, console, options)

    def __rich_measure__(
        self, console: "Console", options: "ConsoleOptions"
    ) -> "Measurement":
        stack: List[Iterator[Tree]] = [iter([self])]
        pop = stack.pop
        push = stack.append
        minimum = 0
        maximum = 0
        measure = Measurement.get
        level = 0
        while stack:
            iter_tree = pop()
            try:
                tree = next(iter_tree)
            except StopIteration:
                level -= 1
                continue
            push(iter_tree)
            min_measure, max_measure = measure(console, options, tree.label)
            indent = level * 4
            minimum = max(min_measure + indent, minimum)
            maximum = max(max_measure + indent, maximum)
            if tree.expanded and tree.children:
                push(iter(tree.children))
                level += 1
        return Measurement(minimum, maximum)


if __name__ == "__main__":  # pragma: no cover
    from rich.console import Group
    from rich.markdown import Markdown
    from rich.panel import Panel
    from rich.syntax import Syntax
    from rich.table import Table

    table = Table(row_styles=["", "dim"])

    table.add_column("Released", style="cyan", no_wrap=True)
    table.add_column("Title", style="magenta")
    table.add_column("Box Office", justify="right", style="green")

    table.add_row("Dec 20, 2019", "Star Wars: The Rise of Skywalker", "$952,110,690")
    table.add_row("May 25, 2018", "Solo: A Star Wars Story", "$393,151,347")
    table.add_row("Dec 15, 2017", "Star Wars Ep. V111: The Last Jedi", "$1,332,539,889")
    table.add_row("Dec 16, 2016", "Rogue One: A Star Wars Story", "$1,332,439,889")

    code = """\
class Segment(NamedTuple):
    text: str = ""
    style: Optional[Style] = None
    is_control: bool = False
"""
    syntax = Syntax(code, "python", theme="monokai", line_numbers=True)

    markdown = Markdown(
        """\
### example.md
> Hello, World!
>
> Markdown _all_ the things
"""
    )

    root = Tree("🌲 [b green]Rich Tree", highlight=True, hide_root=True)

    node = root.add(":file_folder: Renderables", guide_style="red")
    simple_node = node.add(":file_folder: [bold yellow]Atomic", guide_style="uu green")
    simple_node.add(Group("📄 Syntax", syntax))
    simple_node.add(Group("📄 Markdown", Panel(markdown, border_style="green")))

    containers_node = node.add(
        ":file_folder: [bold magenta]Containers", guide_style="bold magenta"
    )
    containers_node.expanded = True
    panel = Panel.fit("Just a panel", border_style="red")
    containers_node.add(Group("📄 Panels", panel))

    containers_node.add(Group("📄 [b magenta]Table", table))

    console = Console()

    console.print(root)
