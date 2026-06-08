"""Layout lookup helpers (extracted for kiss complexity)."""
from __future__ import annotations

from typing import Any, Optional


def find_layout_by_name(root: Any, name: str) -> Optional[Any]:
    """Return the first descendant layout matching *name*, or None."""
    if root.name == name:
        return root
    for child in root._children:
        found = find_layout_by_name(child, name)
        if found is not None:
            return found
    return None
