from typing import Any


class SystemPager:
    """Uses the pager installed on the system."""

    def _pager(self, content: str) -> Any:  #  pragma: no cover
        return __import__("pydoc").pager(content)

    def __call__(self, content: str) -> None:
        """Show content in the system pager."""
        self._pager(content)


Pager = SystemPager
