from ._lazy import import_attr
from functools import partial
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


class ReprError(Exception):
    """An error occurred when attempting to build a repr."""


def _append_repr_arg(repr_str: List[str], arg: Any) -> None:
    """Append one __rich_repr__ argument to repr_str."""
    append = repr_str.append
    if not isinstance(arg, tuple):
        append(repr(arg))
        return
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


def _yield_rich_repr_param(self: Any, param: Any) -> Result:
    """Yield one __init__ parameter for auto_rich_repr."""
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
            angular: bool = getattr(self.__rich_repr__, "angular", False)  # type: ignore[attr-defined]
            for arg in self.__rich_repr__():  # type: ignore[attr-defined]
                _append_repr_arg(repr_str, arg)
            if angular:
                return f"<{self.__class__.__name__} {' '.join(repr_str)}>"
            return f"{self.__class__.__name__}({', '.join(repr_str)})"

        def auto_rich_repr(self: Type[T]) -> Result:
            """Auto generate __rich_rep__ from signature of __init__"""
            try:
                import inspect

                signature = inspect.signature(self.__init__)
                for name, param in signature.parameters.items():
                    yield from _yield_rich_repr_param(self, param)
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


if __name__ == "__main__":

    @auto
    class Foo:
        def __rich_repr__(self) -> Result:
            yield "foo"
            yield "bar", {"shopping": ["eggs", "ham", "pineapple"]}
            yield "buy", "hand sanitizer"

    foo = Foo()
    Console = import_attr('rich.console', 'Console')

    console = Console()

    console.rule("Standard repr")
    console.print(foo)

    console.print(foo, width=60)
    console.print(foo, width=30)

    console.rule("Angular repr")
    Foo.__rich_repr__.angular = True  # type: ignore[attr-defined]

    console.print(foo)

    console.print(foo, width=60)
    console.print(foo, width=30)
