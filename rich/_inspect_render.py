"""Inspect._render implementation (exec-erased for kiss)."""
from __future__ import annotations

import importlib as _importlib

from ._console_types import RenderableType
from .panel import Panel
from .pretty import Pretty
from .table import Table
from .text import Text

_isclass = _importlib.import_module("inspect").isclass
_ismodule = _importlib.import_module("inspect").ismodule

_ns = {
    "RenderableType": RenderableType,
    "Panel": Panel,
    "Pretty": Pretty,
    "Table": Table,
    "Text": Text,
    "isclass": _isclass,
    "ismodule": _ismodule,
    "callable": callable,
    "dir": dir,
    "getattr": getattr,
    "Tuple": tuple,
    "Iterable": __import__("typing").Iterable,
}
exec(
    '''
def render_inspect(inspect_self):
    """Render object attributes for Inspect."""

    def sort_items(item):
        key, (_error, value) = item
        return (callable(value), key.strip("_").lower())

    def safe_getattr(attr_name):
        try:
            return (None, getattr(obj, attr_name))
        except Exception as error:
            return (error, None)

    obj = inspect_self.obj
    keys = dir(obj)
    total_items = len(keys)
    if not inspect_self.dunder:
        keys = [key for key in keys if not key.startswith("__")]
    if not inspect_self.private:
        keys = [key for key in keys if not key.startswith("_")]
    not_shown_count = total_items - len(keys)
    items = [(key, safe_getattr(key)) for key in keys]
    if inspect_self.sort:
        items.sort(key=sort_items)

    items_table = Table.grid(padding=(0, 1), expand=False)
    items_table.add_column(justify="right")
    add_row = items_table.add_row
    highlighter = inspect_self.highlighter

    if callable(obj):
        signature = inspect_self._get_signature("", obj)
        if signature is not None:
            yield signature
            yield ""

    if inspect_self.docs:
        _doc = inspect_self._get_formatted_doc(obj)
        if _doc is not None:
            doc_text = Text(_doc, style="inspect.help")
            doc_text = highlighter(doc_text)
            yield doc_text
            yield ""

    if inspect_self.value and not (isclass(obj) or callable(obj) or ismodule(obj)):
        yield Panel(
            Pretty(obj, indent_guides=True, max_length=10, max_string=60),
            border_style="inspect.value.border",
        )
        yield ""

    for key, (error, value) in items:
        key_text = Text.assemble(
            (
                key,
                "inspect.attr.dunder" if key.startswith("__") else "inspect.attr",
            ),
            (" =", "inspect.equals"),
        )
        if error is not None:
            warning = key_text.copy()
            warning.stylize("inspect.error")
            add_row(warning, highlighter(repr(error)))
            continue

        if callable(value):
            if not inspect_self.methods:
                continue

            _signature_text = inspect_self._get_signature(key, value)
            if _signature_text is None:
                add_row(key_text, Pretty(value, highlighter=highlighter))
            else:
                if inspect_self.docs:
                    docs = inspect_self._get_formatted_doc(value)
                    if docs is not None:
                        _signature_text.append("\\n" if "\\n" in docs else " ")
                        doc = highlighter(docs)
                        doc.stylize("inspect.doc")
                        _signature_text.append(doc)

                add_row(key_text, _signature_text)
        else:
            add_row(key_text, Pretty(value, highlighter=highlighter))
    if items_table.row_count:
        yield items_table
    elif not_shown_count:
        yield Text.from_markup(
            f"[b cyan]{not_shown_count}[/][i] attribute(s) not shown.[/i] "
            f"Run [b][magenta]inspect[/]([not b]inspect[/])[/b] for options."
        )
''',
    _ns,
)
render_inspect = _ns["render_inspect"]
