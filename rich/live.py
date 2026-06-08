from __future__ import annotations

import sys
from threading import RLock
from types import TracebackType
from typing import IO, TYPE_CHECKING, Any, Callable, List, Optional, TextIO, Type, cast

from ._get_console import _fetch_global_console as get_console
from ._live_refresh_thread import RefreshThread
from ._group_registry import Group
from .control import Control
from .file_proxy import FileProxy
from .jupyter import JupyterMixin
from .live_render import LiveRender, VerticalOverflowMethod
from .screen import Screen
from ._render_protocol import Console, ConsoleRenderable, RenderHook, RenderableType

if TYPE_CHECKING:
    # Can be replaced with `from typing import Self` in Python 3.11+
    from typing_extensions import Self  # pragma: no cover


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

        self._refresh_thread: Optional[RefreshThread] = None
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

    def _start_refresh_thread(self) -> None:
        if not self.auto_refresh:
            return
        self._refresh_thread = RefreshThread(
            self.refresh, self.refresh_per_second, self._lock
        )
        self._refresh_thread.start()

    def _on_start_refresh_error(self) -> None:
        self.stop()

    def _activate_live(self, refresh: bool) -> None:
        if not self.console.set_live(self):
            self._nested = True
            return

        if self._screen:
            self._alt_screen = self.console.set_alt_screen(True)
        self.console.show_cursor(False)
        self._enable_redirect_io()
        self.console.push_render_hook(self)
        if refresh:
            try:
                self.refresh()
            except Exception:
                self._on_start_refresh_error()
                raise
        self._start_refresh_thread()

    def start(self, refresh: bool = False) -> None:
        """Start live rendering display.

        Args:
            refresh (bool, optional): Also refresh. Defaults to False.
        """
        with self._lock:
            if self._started:
                return
            self._started = True
            self._activate_live(refresh)

    def _stop_refresh_thread(self) -> None:
        if not (self.auto_refresh and self._refresh_thread is not None):
            return
        self._refresh_thread.stop()
        self._refresh_thread = None

    def _restore_terminal_after_stop(self) -> None:
        if not self._alt_screen and self.console.is_terminal and self._live_render.last_render_height:
            self.console.line()
        self.console.show_cursor(True)
        if self._alt_screen:
            self.console.set_alt_screen(False)
        if self.transient and not self._alt_screen:
            self.console.control(self._live_render.restore_cursor())
        if self.ipy_widget is not None and self.transient:
            self.ipy_widget.close()  # pragma: no cover

    def _finalize_stop(self) -> None:
        self.vertical_overflow = "visible"
        with self.console:
            try:
                if not self._alt_screen and not self.console.is_jupyter:
                    self.refresh()
            finally:
                self._disable_redirect_io()
                self.console.pop_render_hook()
                self._restore_terminal_after_stop()

    def stop(self) -> None:
        """Stop live rendering display."""
        with self._lock:
            if not self._started:
                return
            self._started = False
            self.console.clear_live()
            if self._nested:
                if not self.transient:
                    self.console.print(self.renderable)
                return

            self._stop_refresh_thread()
            self._finalize_stop()

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

    def _refresh_jupyter(self) -> None:
        try:
            from IPython.display import display
            from ipywidgets import Output
        except ImportError:
            import warnings

            warnings.warn('install "ipywidgets" for Jupyter support')
            return

        if self.ipy_widget is None:
            self.ipy_widget = Output()
            display(self.ipy_widget)

        with self.ipy_widget:
            self.ipy_widget.clear_output(wait=True)
            self.console.print(self._live_render.renderable)

    def _refresh_terminal(self) -> None:
        if self.console.is_terminal and not self.console.is_dumb_terminal:
            with self.console:
                self.console.print(Control())
            return
        if not self._started and not self.transient:
            with self.console:
                self.console.print(Control())

    def refresh(self) -> None:
        """Update the display of the Live Render."""
        with self._lock:
            self._live_render.set_renderable(self.renderable)
            if self._nested:
                if self.console._live_stack:
                    self.console._live_stack[0].refresh()
                return

            if self.console.is_jupyter:  # pragma: no cover
                self._refresh_jupyter()
            else:
                self._refresh_terminal()

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
