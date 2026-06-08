from functools import partial
import inspect
from typing import (
    Any,
    Callable,
    Iterable,
    List,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
    overload,
)

T = TypeVar("T")


Result = Iterable[Union[Any, Tuple[Any], Tuple[str, Any], Tuple[str, Any, Any]]]
RichReprResult = Result

ReprError = type(
    "ReprError", (Exception,), {"__doc__": "An error occurred when attempting to build a repr."}
)


def _repr_append_arg(append: Callable[[str], None], arg: object) -> None:
    if isinstance(arg, tuple):
        if len(arg) == 1:
            append(repr(arg[0]))
            return
        key, value, *default = arg
        if key is None:
            append(repr(value))
            return
        if default and default[0] == value:
            return
        append(f"{key}={value!r}")
        return
    append(repr(arg))


def _repr_build_string(cls_name: str, repr_str: List[str], angular: bool) -> str:
    if angular:
        return f"<{cls_name} {' '.join(repr_str)}>"
    return f"{cls_name}({', '.join(repr_str)})"


def _yield_param_rich_repr(obj: object, param: inspect.Parameter) -> object:
    if param.kind == param.POSITIONAL_ONLY:
        return getattr(obj, param.name)
    if param.kind in (param.POSITIONAL_OR_KEYWORD, param.KEYWORD_ONLY):
        if param.default is param.empty:
            return getattr(obj, param.name)
        return param.name, getattr(obj, param.name), param.default
    return None


def _iter_init_rich_repr(obj: object) -> Result:
    signature = inspect.signature(obj.__init__)
    for name, param in signature.parameters.items():
        value = _yield_param_rich_repr(obj, param)
        if value is not None:
            yield value


@overload
def auto(cls: Optional[Type[T]]) -> Type[T]:
    ...


@overload
def auto(*, angular: bool = False) -> Callable[[Type[T]], Type[T]]:
    ...


def auto(
    cls: Optional[Type[T]] = None, *, angular: Optional[bool] = None
) -> Union[Type[T], Callable[[Type[T]], Type[T]]]:
    """Class decorator to create __repr__ from __rich_repr__"""

    def do_replace(cls: Type[T], angular: Optional[bool] = None) -> Type[T]:
        def auto_repr(self: T) -> str:
            """Create repr string from __rich_repr__"""
            repr_str: List[str] = []
            append = repr_str.append
            angular: bool = getattr(self.__rich_repr__, "angular", False)  # type: ignore[attr-defined]
            for arg in self.__rich_repr__():  # type: ignore[attr-defined]
                _repr_append_arg(append, arg)
            return _repr_build_string(self.__class__.__name__, repr_str, angular)

        def auto_rich_repr(self: Type[T]) -> Result:
            """Auto generate __rich_rep__ from signature of __init__"""
            try:
                yield from _iter_init_rich_repr(self)
            except Exception as error:
                raise ReprError(
                    f"Failed to auto generate __rich_repr__; {error}"
                ) from None

        if not hasattr(cls, "__rich_repr__"):
            auto_rich_repr.__doc__ = "Build a rich repr"
            cls.__rich_repr__ = auto_rich_repr  # type: ignore[attr-defined]

        auto_repr.__doc__ = "Return repr(self)"
        cls.__repr__ = auto_repr  # type: ignore[assignment]
        if angular is not None:
            cls.__rich_repr__.angular = angular  # type: ignore[attr-defined]
        return cls

    if cls is None:
        return partial(do_replace, angular=angular)
    else:
        return do_replace(cls, angular=angular)


@overload
def rich_repr(cls: Optional[Type[T]]) -> Type[T]:
    ...


@overload
def rich_repr(*, angular: bool = False) -> Callable[[Type[T]], Type[T]]:
    ...


def rich_repr(
    cls: Optional[Type[T]] = None, *, angular: bool = False
) -> Union[Type[T], Callable[[Type[T]], Type[T]]]:
    if cls is None:
        return auto(angular=angular)
    else:
        return auto(cls)


