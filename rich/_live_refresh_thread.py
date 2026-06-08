from threading import Event, RLock, Thread
from typing import Callable, Optional


class RefreshThread(Thread):
    """A thread that calls a refresh callback at regular intervals."""

    def __init__(
        self,
        refresh: Callable[[], None],
        refresh_per_second: float,
        lock: Optional[RLock] = None,
    ) -> None:
        self._refresh = refresh
        self.refresh_per_second = refresh_per_second
        self._lock = lock
        self.done = Event()
        super().__init__(daemon=True)

    def stop(self) -> None:
        self.done.set()

    def _do_refresh(self) -> None:
        if self._lock is not None:
            with self._lock:
                if not self.done.is_set():
                    self._refresh()
        elif not self.done.is_set():
            self._refresh()

    def run(self) -> None:
        while not self.done.wait(1 / self.refresh_per_second):
            if self.done.is_set():
                continue
            self._do_refresh()
