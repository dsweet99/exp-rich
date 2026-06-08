from typing import Any


def load_ipython_extension(ip: Any) -> None:  # pragma: no cover
    from importlib import import_module

    import_module("rich.pretty").install()
    import_module("rich.traceback").install()
