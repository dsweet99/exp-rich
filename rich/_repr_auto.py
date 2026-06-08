from typing import List, Type, TypeVar

from ._repr_error import ReprError
from ._repr_result import Result

T = TypeVar("T")


def _append_tuple_repr_arg(repr_str: List[str], arg: tuple) -> None:
    if len(arg) == 1:
        repr_str.append(repr(arg[0]))
        return
    key, value, *default = arg
    if key is None:
        repr_str.append(repr(value))
        return
    if default and default[0] == value:
        return
    repr_str.append(f"{key}={value!r}")


def format_rich_repr_arg(repr_str: List[str], arg: object) -> None:
    """Append one __rich_repr__ yield value to repr_str."""
    if isinstance(arg, tuple):
        _append_tuple_repr_arg(repr_str, arg)
    else:
        repr_str.append(repr(arg))


def build_auto_repr(self: T, angular: bool) -> str:
    """Create repr string from __rich_repr__."""
    repr_str: List[str] = []
    for arg in self.__rich_repr__():  # type: ignore[attr-defined]
        format_rich_repr_arg(repr_str, arg)
    if angular:
        return f"<{self.__class__.__name__} {' '.join(repr_str)}>"
    return f"{self.__class__.__name__}({', '.join(repr_str)})"


def _yield_init_param(self: Type[T], param: object) -> Result:
    import inspect

    if param.kind == inspect.Parameter.POSITIONAL_ONLY:
        yield getattr(self, param.name)
        return
    if param.kind not in (
        inspect.Parameter.POSITIONAL_OR_KEYWORD,
        inspect.Parameter.KEYWORD_ONLY,
    ):
        return
    if param.default is inspect.Parameter.empty:
        yield getattr(self, param.name)
        return
    yield param.name, getattr(self, param.name), param.default


def iter_auto_rich_repr(self: Type[T]) -> Result:
    """Auto generate __rich_rep__ from signature of __init__."""
    try:
        import inspect

        signature = inspect.signature(self.__init__)
        for name, param in signature.parameters.items():
            yield from _yield_init_param(self, param)
    except Exception as error:
        raise ReprError(
            f"Failed to auto generate __rich_repr__; {error}"
        ) from None
