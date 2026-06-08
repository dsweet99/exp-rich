from __future__ import annotations

from types import TracebackType
from typing import Optional, Type, TYPE_CHECKING

from ._jupyter_mixin import JupyterMixin
from ._pick import M_CONSOLE, M_LIVE, M_SPINNER, rich_module
from .style import StyleType

if TYPE_CHECKING:
    from ._types import Console, RenderableType



class Status(JupyterMixin):
    """Displays a status indicator with a 'spinner' animation.

    Args:
        status (RenderableType): A status renderable (str or Text typically).
        console (Console, optional): Console instance to use, or None for global console. Defaults to None.
        spinner (str, optional): Name of spinner animation (see python -m rich.spinner). Defaults to "dots".
        spinner_style (StyleType, optional): Style of spinner. Defaults to "status.spinner".
        speed (float, optional): Speed factor for spinner animation. Defaults to 1.0.
        refresh_per_second (float, optional): Number of refreshes per second. Defaults to 12.5.
    """

    def __init__(
        self,
        status: "RenderableType",
        *,
        console: Optional["Console"] = None,
        spinner: str = "dots",
        spinner_style: StyleType = "status.spinner",
        speed: float = 1.0,
        refresh_per_second: float = 12.5,
    ):
        Spinner = rich_module(M_SPINNER).Spinner
        Live = rich_module(M_LIVE).Live
        self.status = status
        self.spinner_style = spinner_style
        self.speed = speed
        self._spinner = Spinner(spinner, text=status, style=spinner_style, speed=speed)
        self._live = Live(
            self.renderable,
            console=console,
            refresh_per_second=refresh_per_second,
            transient=True,
        )

    @property
    def renderable(self):
        return self._spinner

    @property
    def console(self) -> "Console":
        return self._live.console

    def update(
        self,
        status: Optional["RenderableType"] = None,
        *,
        spinner: Optional[str] = None,
        spinner_style: Optional[StyleType] = None,
        speed: Optional[float] = None,
    ) -> None:
        """Update status.

        Args:
            status (Optional[RenderableType], optional): New status renderable or None for no change. Defaults to None.
            spinner (Optional[str], optional): New spinner or None for no change. Defaults to None.
            spinner_style (Optional[StyleType], optional): New spinner style or None for no change. Defaults to None.
            speed (Optional[float], optional): Speed factor for spinner animation or None for no change. Defaults to None.
        """
        if status is not None:
            self.status = status
        if spinner_style is not None:
            self.spinner_style = spinner_style
        if spinner is not None:
            self._spinner = rich_module(M_SPINNER).Spinner(
                spinner,
                text=self.status,
                style=self.spinner_style,
                speed=speed or self.speed,
            )
        elif speed is not None:
            self._spinner.update(speed=speed)
        if any(arg is not None for arg in (status, spinner, spinner_style, speed)):
            self._live.update(self.renderable, refresh=True)

    def start(self) -> None:
        """Start the status animation."""
        self._live.start()

    def stop(self) -> None:
        """Stop the spinner animation."""
        self._live.stop()

    def __rich__(self) -> "RenderableType":
        return self.renderable

    def __enter__(self) -> "Status":
        self.start()
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        self.stop()


if __name__ == "__main__":  # pragma: no cover
    from time import sleep

    console = rich_module(M_CONSOLE).Console()
    with console.status("[magenta]Covid detector booting up") as status:
        sleep(3)
        status.update("[bold yellow]Detecting Covid")
        sleep(3)
    console.print("[bold green]Covid not detected")
