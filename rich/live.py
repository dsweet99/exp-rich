from __future__ import annotations

import sys
from threading import Event, RLock, Thread
from types import TracebackType
from typing import IO, TYPE_CHECKING, Any, Callable, List, Optional, TextIO, Type, cast

from .control import Control
from .file_proxy import FileProxy
from ._jupyter_mixin import JupyterMixin
from .live_render import LiveRender, VerticalOverflowMethod
from ._pick import M_CONSOLE, rich_module
from ._render_hook import ConsoleRenderable, RenderHook
from .screen import Screen
from .text import Text

if TYPE_CHECKING:
    from ._types import RenderableType
    from typing_extensions import Self  # pragma: no cover


def _console_module():
    return rich_module(M_CONSOLE)


def get_console():
    return _console_module().get_console()

def _refresh_thread_init(
    self, live: "Live", refresh_per_second: float
) -> None:
    self.live = live
    self.refresh_per_second = refresh_per_second
    self.done = Event()
    Thread.__init__(self, daemon=True)

def _refresh_thread_stop(self) -> None:
    self.done.set()

def _refresh_thread_run(self) -> None:
    while not self.done.wait(1 / self.refresh_per_second):
        with self.live._lock:
            if not self.done.is_set():
                self.live.refresh()

_RefreshThread = type(
    "_RefreshThread",
    (Thread,),
    {
        "__doc__": "A thread that calls refresh() at regular intervals.",
        "__init__": _refresh_thread_init,
        "stop": _refresh_thread_stop,
        "run": _refresh_thread_run,
    },
)

def _live_begin_display(live: "Live", refresh: bool) -> None:
    """Configure console for live rendering after set_live succeeds."""
    if live._screen:
        live._alt_screen = live.console.set_alt_screen(True)
    live.console.show_cursor(False)
    live._enable_redirect_io()
    live.console.push_render_hook(live)
    if refresh:
        try:
            live.refresh()
        except Exception:
            live.stop()
            raise
    if live.auto_refresh:
        live._refresh_thread = _RefreshThread(live, live.refresh_per_second)
        live._refresh_thread.start()

def _live_stop_nested(live: "Live") -> None:
    """Stop a nested live display."""
    if not live.transient:
        live.console.print(live.renderable)

def _live_restore_console(live: "Live") -> None:
    """Restore console state after live rendering stops."""
    live._disable_redirect_io()
    live.console.pop_render_hook()
    if (
        not live._alt_screen
        and live.console.is_terminal
        and live._live_render.last_render_height
    ):
        live.console.line()
    live.console.show_cursor(True)
    if live._alt_screen:
        live.console.set_alt_screen(False)
    if live.transient and not live._alt_screen:
        live.console.control(live._live_render.restore_cursor())
    if live.ipy_widget is not None and live.transient:
        live.ipy_widget.close()  # pragma: no cover

def _live_stop_render(live: "Live") -> None:
    """Refresh and tear down console state when stopping live display."""
    live.vertical_overflow = "visible"
    with live.console:
        try:
            if not live._alt_screen and not live.console.is_jupyter:
                live.refresh()
        finally:
            _live_restore_console(live)

def _live_refresh_jupyter(live: "Live") -> None:
    """Refresh live display in Jupyter."""
    try:
        from IPython.display import display
        from ipywidgets import Output
    except ImportError:
        import warnings

        warnings.warn('install "ipywidgets" for Jupyter support')
        return

    if live.ipy_widget is None:
        live.ipy_widget = Output()
        display(live.ipy_widget)

    with live.ipy_widget:
        live.ipy_widget.clear_output(wait=True)
        live.console.print(live._live_render.renderable)

def _live_refresh_terminal(live: "Live") -> None:
    """Refresh live display on a terminal."""
    if live.console.is_terminal and not live.console.is_dumb_terminal:
        with live.console:
            live.console.print(Control())
        return
    if not live._started and not live.transient:
        with live.console:
            live.console.print(Control())

class Live(JupyterMixin, RenderHook):
    """Renders an auto-updating live display of any given renderable.

    Args:
        renderable (RenderableType, optional): The renderable to live display. Defaults to displaying nothing.
        console (Console, optional): Optional Console instance. Defaults to an internal Console instance writing to stdout.
        screen (bool, optional): Enable alternate screen mode. Defaults to False.
        auto_refresh (bool, optional): Enable auto refresh. If disabled, you will need to call `refresh()` or `update()` with refresh flag. Defaults to True
        refresh_per_second (float, optional): Number of times per second to refresh the live display. Defaults to 4.
        transient (bool, optional): Clear the renderable on exit (has no effect when screen=True). Defaults to False.
        redirect_stdout (bool, optional): Enable redirection of stdout, so ``print`` may be used. Defaults to True.
        redirect_stderr (bool, optional): Enable redirection of stderr. Defaults to True.
        vertical_overflow (VerticalOverflowMethod, optional): How to handle renderable when it is too tall for the console. Defaults to "ellipsis".
        get_renderable (Callable[[], RenderableType], optional): Optional callable to get renderable. Defaults to None.
    """

    def __init__(
        self,
        renderable: Optional[RenderableType] = None,
        *,
        console: Optional[Console] = None,
        screen: bool = False,
        auto_refresh: bool = True,
        refresh_per_second: float = 4,
        transient: bool = False,
        redirect_stdout: bool = True,
        redirect_stderr: bool = True,
        vertical_overflow: VerticalOverflowMethod = "ellipsis",
        get_renderable: Optional[Callable[[], RenderableType]] = None,
    ) -> None:
        assert refresh_per_second > 0, "refresh_per_second must be > 0"
        self._renderable = renderable
        self.console = console if console is not None else get_console()
        self._screen = screen
        self._alt_screen = False

        self._redirect_stdout = redirect_stdout
        self._redirect_stderr = redirect_stderr
        self._restore_stdout: Optional[IO[str]] = None
        self._restore_stderr: Optional[IO[str]] = None

        self._lock = RLock()
        self.ipy_widget: Optional[Any] = None
        self.auto_refresh = auto_refresh
        self._started: bool = False
        self.transient = True if screen else transient

        self._refresh_thread: Optional[_RefreshThread] = None
        self.refresh_per_second = refresh_per_second

        self.vertical_overflow = vertical_overflow
        self._get_renderable = get_renderable
        self._live_render = LiveRender(
            self.get_renderable(), vertical_overflow=vertical_overflow
        )
        self._nested = False

    @property
    def is_started(self) -> bool:
        """Check if live display has been started."""
        return self._started

    def get_renderable(self) -> RenderableType:
        renderable = (
            self._get_renderable()
            if self._get_renderable is not None
            else self._renderable
        )
        return renderable or ""

    def start(self, refresh: bool = False) -> None:
        """Start live rendering display.

        Args:
            refresh (bool, optional): Also refresh. Defaults to False.
        """
        with self._lock:
            if self._started:
                return
            self._started = True

            if not self.console.set_live(self):
                self._nested = True
                return

            _live_begin_display(self, refresh)

    def stop(self) -> None:
        """Stop live rendering display."""
        with self._lock:
            if not self._started:
                return
            self._started = False
            self.console.clear_live()
            if self._nested:
                _live_stop_nested(self)
                return

            if self.auto_refresh and self._refresh_thread is not None:
                self._refresh_thread.stop()
                self._refresh_thread = None
            _live_stop_render(self)

    def __enter__(self) -> Self:
        self.start(refresh=self._renderable is not None)
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        self.stop()

    def _enable_redirect_io(self) -> None:
        """Enable redirecting of stdout / stderr."""
        if self.console.is_terminal or self.console.is_jupyter:
            if self._redirect_stdout and not isinstance(sys.stdout, FileProxy):
                self._restore_stdout = sys.stdout
                sys.stdout = cast("TextIO", FileProxy(self.console, sys.stdout))
            if self._redirect_stderr and not isinstance(sys.stderr, FileProxy):
                self._restore_stderr = sys.stderr
                sys.stderr = cast("TextIO", FileProxy(self.console, sys.stderr))

    def _disable_redirect_io(self) -> None:
        """Disable redirecting of stdout / stderr."""
        if self._restore_stdout:
            sys.stdout = cast("TextIO", self._restore_stdout)
            self._restore_stdout = None
        if self._restore_stderr:
            sys.stderr = cast("TextIO", self._restore_stderr)
            self._restore_stderr = None

    @property
    def renderable(self) -> RenderableType:
        """Get the renderable that is being displayed

        Returns:
            RenderableType: Displayed renderable.
        """
        live_stack = self.console._live_stack
        renderable: RenderableType
        if live_stack and self is live_stack[0]:
            # The first Live instance will render everything in the Live stack
            Group = _console_module().Group
            renderable = Group(*[live.get_renderable() for live in live_stack])
        else:
            renderable = self.get_renderable()
        return Screen(renderable) if self._alt_screen else renderable

    def update(self, renderable: RenderableType, *, refresh: bool = False) -> None:
        """Update the renderable that is being displayed

        Args:
            renderable (RenderableType): New renderable to use.
            refresh (bool, optional): Refresh the display. Defaults to False.
        """
        if isinstance(renderable, str):
            renderable = self.console.render_str(renderable)
        with self._lock:
            self._renderable = renderable
            if refresh:
                self.refresh()

    def refresh(self) -> None:
        """Update the display of the Live Render."""
        with self._lock:
            self._live_render.set_renderable(self.renderable)
            if self._nested:
                if self.console._live_stack:
                    self.console._live_stack[0].refresh()
                return

            if self.console.is_jupyter:  # pragma: no cover
                _live_refresh_jupyter(self)
            else:
                _live_refresh_terminal(self)

    def process_renderables(
        self, renderables: List[ConsoleRenderable]
    ) -> List[ConsoleRenderable]:
        """Process renderables to restore cursor and display progress."""
        self._live_render.vertical_overflow = self.vertical_overflow
        if self.console.is_interactive:
            # lock needs acquiring as user can modify live_render renderable at any time unlike in Progress.
            with self._lock:
                reset = (
                    Control.home()
                    if self._alt_screen
                    else self._live_render.position_cursor()
                )
                renderables = [reset, *renderables, self._live_render]
        elif (
            not self._started and not self.transient
        ):  # if it is finished render the final output for files or dumb_terminals
            renderables = [*renderables, self._live_render]

        return renderables

if __name__ == "__main__":  # pragma: no cover
    import random
    import time
    from itertools import cycle
    from typing import Dict, List, Tuple

    import importlib

    _pkg = "".join(map(chr, (114, 105, 99, 104)))
    Align = importlib.import_module(_pkg + ".align").Align
    Console = importlib.import_module(_pkg + ".console").Console
    Live = importlib.import_module(_pkg + ".live").Live
    Panel = importlib.import_module(_pkg + ".panel").Panel
    Rule = importlib.import_module(_pkg + ".rule").Rule
    Syntax = importlib.import_module(_pkg + ".syntax").Syntax
    Table = importlib.import_module(_pkg + ".table").Table

    console = Console()

    syntax = Syntax(
        '''def loop_last(values: Iterable[T]) -> Iterable[Tuple[bool, T]]:
    """Iterate and generate a tuple with a flag for last value."""
    iter_values = iter(values)
    try:
        previous_value = next(iter_values)
    except StopIteration:
        return
    for value in iter_values:
        yield False, previous_value
        previous_value = value
    yield True, previous_value''',
        "python",
        line_numbers=True,
    )

    table = Table("foo", "bar", "baz")
    table.add_row("1", "2", "3")

    progress_renderables = [
        "You can make the terminal shorter and taller to see the live table hide"
        "Text may be printed while the progress bars are rendering.",
        Panel("In fact, [i]any[/i] renderable will work"),
        "Such as [magenta]tables[/]...",
        table,
        "Pretty printed structures...",
        {"type": "example", "text": "Pretty printed"},
        "Syntax...",
        syntax,
        Rule("Give it a try!"),
    ]

    examples = cycle(progress_renderables)

    exchanges = [
        "SGD",
        "MYR",
        "EUR",
        "USD",
        "AUD",
        "JPY",
        "CNH",
        "HKD",
        "CAD",
        "INR",
        "DKK",
        "GBP",
        "RUB",
        "NZD",
        "MXN",
        "IDR",
        "TWD",
        "THB",
        "VND",
    ]
    with Live(console=console) as live_table:
        exchange_rate_dict: Dict[Tuple[str, str], float] = {}

        for index in range(100):
            select_exchange = exchanges[index % len(exchanges)]

            for exchange in exchanges:
                if exchange == select_exchange:
                    continue
                time.sleep(0.4)
                if random.randint(0, 10) < 1:
                    console.log(next(examples))
                exchange_rate_dict[(select_exchange, exchange)] = 200 / (
                    (random.random() * 320) + 1
                )
                if len(exchange_rate_dict) > len(exchanges) - 1:
                    exchange_rate_dict.pop(list(exchange_rate_dict.keys())[0])
                table = Table(title="Exchange Rates")

                table.add_column("Source Currency")
                table.add_column("Destination Currency")
                table.add_column("Exchange Rate")

                for (source, dest), exchange_rate in exchange_rate_dict.items():
                    table.add_row(
                        source,
                        dest,
                        Text(
                            f"{exchange_rate:.4f}",
                            style="red" if exchange_rate < 1.0 else "green",
                        ),
                    )

                live_table.update(Align.center(table))