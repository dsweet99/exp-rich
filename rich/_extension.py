import importlib as _importlib
from typing import Any


def load_ipython_extension(ip: Any) -> None:  # pragma: no cover
    # prevent circular import
    install = _importlib.import_module(".pretty", __package__).install
    tr_install = _importlib.import_module(".traceback", __package__).install

    install()
    tr_install()
