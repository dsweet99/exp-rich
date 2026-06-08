import importlib as _importlib


def _fetch_global_console():
    """Return the global console without a static import of ``rich.__init__``."""
    return _importlib.import_module("rich").get_console()
