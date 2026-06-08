from __future__ import annotations

from ._lazy import import_attr
DEFAULT_STYLES = import_attr('rich.default_styles', 'DEFAULT_STYLES')
Theme = import_attr('rich.theme', 'Theme')


DEFAULT = Theme(DEFAULT_STYLES)
