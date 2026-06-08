from abc import ABC, abstractmethod
from typing import List


class RenderHook(ABC):
    """Provides hooks in to the render process."""

    @abstractmethod
    def process_renderables(self, renderables: List[object]) -> List[object]:
        """Called with a list of objects to render."""


ConsoleRenderable = object
