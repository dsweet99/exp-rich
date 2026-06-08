from __future__ import annotations

from typing import Any, Optional

from .measure import Measurement


def measure_fixed_width(
    width: Optional[int], options: Any, *, default_min: int = 4
) -> Measurement:
    """Return measurement for a renderable with an optional fixed width."""
    if width is not None:
        return Measurement(width, width)
    return Measurement(default_min, options.max_width)
