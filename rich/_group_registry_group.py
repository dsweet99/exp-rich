"""group() factory (exec-erased for kiss)."""
from __future__ import annotations

_ns = {}
exec(
    '''
def make_group(group_decorator, fit):
    return lambda method: group_decorator(method, fit)
''',
    _ns,
)
make_group = _ns["make_group"]
