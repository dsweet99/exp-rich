from __future__ import annotations

from ._lazy import import_attr
from typing import Callable, Iterator, List, Optional, Tuple

loop_first = import_attr('rich._loop', 'loop_first')
loop_last = import_attr('rich._loop', 'loop_last')
Console = import_attr('rich.console', 'Console')
ConsoleOptions = import_attr('rich.console', 'ConsoleOptions')
RenderableType = import_attr('rich.console', 'RenderableType')
RenderResult = import_attr('rich.console', 'RenderResult')
JupyterMixin = import_attr('rich.jupyter', 'JupyterMixin')
Measurement = import_attr('rich.measure', 'Measurement')
Segment = import_attr('rich.segment', 'Segment')
Style = import_attr('rich.style', 'Style')
StyleStack = import_attr('rich.style', 'StyleStack')
StyleType = import_attr('rich.style', 'StyleType')
Styled = import_attr('rich.styled', 'Styled')

GuideType = Tuple[str, str, str, str]


def _tree_make_guide(
    tree: "Tree",
    index: int,
    style: Style,
    *,
    ascii_only: bool,
    legacy_windows: bool,
) -> Segment:
    if ascii_only:
        line = tree.ASCII_GUIDES[index]
    else:
        guide = 1 if style.bold else (2 if style.underline2 else 0)
        line = tree.TREE_GUIDES[0 if legacy_windows else guide][index]
    return Segment(line, style)


def _tree_render_node(
    node: "Tree",
    *,
    console: Console,
    options: ConsoleOptions,
    prefix: List[Segment],
    style: Style,
    highlight: bool,
    remove_guide_styles: Style,
    new_line: Segment,
    last: bool,
    hide_root: bool,
    depth: int,
    make_guide: Callable[..., Segment],
) -> RenderResult:
    if depth == 0 and hide_root:
        return
    renderable_lines = console.render_lines(
        Styled(node.label, style),
        options.update(
            width=options.max_width - sum(level.cell_length for level in prefix),
            highlight=highlight,
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
                0 if last else 1,
                prefix[-1].style or Style.null(),
            )


def _tree_pop_node(
    stack_node: Iterator[Tuple[bool, "Tree"]],
    *,
    levels: List[Segment],
    guide_style_stack: StyleStack,
    style_stack: StyleStack,
    make_guide: Callable[..., Segment],
    null_style: Style,
    FORK: int,
) -> Optional[Tuple[bool, "Tree"]]:
    try:
        return next(stack_node)
    except StopIteration:
        levels.pop()
        if levels:
            guide_style = levels[-1].style or null_style
            levels[-1] = make_guide(FORK, guide_style)
            guide_style_stack.pop()
            style_stack.pop()
        return None


def _tree_walk_stack(
    tree: "Tree",
    *,
    stack: List[Iterator[Tuple[bool, Tree]]],
    levels: List[Segment],
    guide_style_stack: StyleStack,
    style_stack: StyleStack,
    console: Console,
    options: ConsoleOptions,
    remove_guide_styles: Style,
    new_line: Segment,
    make_guide: Callable[..., Segment],
    get_style: Callable[..., Style],
    null_style: Style,
    SPACE: int,
    CONTINUE: int,
    FORK: int,
    END: int,
) -> RenderResult:
    pop = stack.pop
    push = stack.append
    depth = 0
    while stack:
        stack_node = pop()
        node_info = _tree_pop_node(
            stack_node,
            levels=levels,
            guide_style_stack=guide_style_stack,
            style_stack=style_stack,
            make_guide=make_guide,
            null_style=null_style,
            FORK=FORK,
        )
        if node_info is None:
            continue
        last, node = node_info
        push(stack_node)
        if last:
            levels[-1] = make_guide(END, levels[-1].style or null_style)

        guide_style = guide_style_stack.current + get_style(node.guide_style)
        style = style_stack.current + get_style(node.style)
        prefix = levels[(2 if tree.hide_root else 1) :]
        yield from _tree_render_node(
            node,
            console=console,
            options=options,
            prefix=prefix,
            style=style,
            highlight=tree.highlight,
            remove_guide_styles=remove_guide_styles,
            new_line=new_line,
            last=last,
            hide_root=tree.hide_root,
            depth=depth,
            make_guide=make_guide,
        )

        if node.expanded and node.children:
            levels[-1] = make_guide(
                SPACE if last else CONTINUE, levels[-1].style or null_style
            )
            levels.append(
                make_guide(END if len(node.children) == 1 else FORK, guide_style)
            )
            style_stack.push(get_style(node.style))
            guide_style_stack.push(get_style(node.guide_style))
            push(iter(loop_last(node.children)))
            depth += 1


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
        stack: List[Iterator[Tuple[bool, Tree]]] = []
        push = stack.append
        new_line = Segment.line()

        get_style = console.get_style
        null_style = Style.null()
        guide_style = get_style(self.guide_style, default="") or null_style
        SPACE, CONTINUE, FORK, END = range(4)

        def make_guide(index: int, style: Style) -> Segment:
            return _tree_make_guide(
                self,
                index,
                style,
                ascii_only=options.ascii_only,
                legacy_windows=options.legacy_windows,
            )

        levels: List[Segment] = [make_guide(CONTINUE, guide_style)]
        push(iter(loop_last([self])))

        guide_style_stack = StyleStack(get_style(self.guide_style))
        style_stack = StyleStack(get_style(self.style))
        remove_guide_styles = Style(bold=False, underline2=False)

        yield from _tree_walk_stack(
            self,
            stack=stack,
            levels=levels,
            guide_style_stack=guide_style_stack,
            style_stack=style_stack,
            console=console,
            options=options,
            remove_guide_styles=remove_guide_styles,
            new_line=new_line,
            make_guide=make_guide,
            get_style=get_style,
            null_style=null_style,
            SPACE=SPACE,
            CONTINUE=CONTINUE,
            FORK=FORK,
            END=END,
        )

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
    Group = import_attr('rich.console', 'Group')
    Markdown = import_attr('rich.markdown', 'Markdown')
    Panel = import_attr('rich.panel', 'Panel')
    Syntax = import_attr('rich.syntax', 'Syntax')
    Table = import_attr('rich.table', 'Table')

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
