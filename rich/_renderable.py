from typing import Any, Set, cast

_GIBBERISH = """aihwerij235234ljsdnp34ksodfipwoe234234jlskjdf"""


def is_renderable(check_object: Any) -> bool:
    """Check if an object may be rendered by Rich."""
    return (
        isinstance(check_object, str)
        or hasattr(check_object, "__rich__")
        or hasattr(check_object, "__rich_console__")
    )


def rich_cast(renderable: object) -> Any:
    """Cast an object to a renderable by calling __rich__ if present."""
    rich_visited_set: Set[type] = set()
    while hasattr(renderable, "__rich__") and not isinstance(renderable, type):
        if hasattr(renderable, _GIBBERISH):
            return repr(renderable)
        cast_method = getattr(renderable, "__rich__")
        renderable = cast_method()
        renderable_type = type(renderable)
        if renderable_type in rich_visited_set:
            break
        rich_visited_set.add(renderable_type)
    return cast(Any, renderable)
