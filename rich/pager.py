from ._lazy import import_attr
from abc import ABC, abstractmethod
from typing import Any


class Pager(ABC):
    """Base class for a pager."""

    @abstractmethod
    def show(self, content: str) -> None:
        """Show content in pager.

        Args:
            content (str): Content to be displayed.
        """


class SystemPager(Pager):
    """Uses the pager installed on the system."""

    def _pager(self, content: str) -> Any:  #  pragma: no cover
        return __import__("pydoc").pager(content)

    def show(self, content: str) -> None:
        """Use the same pager used by pydoc."""
        self._pager(content)


if __name__ == "__main__":  # pragma: no cover
    make_test_card = import_attr('rich.__main__', 'make_test_card')
    Console = import_attr('rich.console', 'Console')

    console = Console()
    with console.pager(styles=True):
        console.print(make_test_card())
