from pathlib import Path
import json as _stdlib_json
from typing import Any, Callable, Optional, Union


class JSON:
    """A renderable which pretty prints JSON.

    Args:
        json (str): JSON encoded data.
        indent (Union[None, int, str], optional): Number of characters to indent by. Defaults to 2.
        highlight (bool, optional): Enable highlighting. Defaults to True.
        skip_keys (bool, optional): Skip keys not of a basic type. Defaults to False.
        ensure_ascii (bool, optional): Escape all non-ascii characters. Defaults to False.
        check_circular (bool, optional): Check for circular references. Defaults to True.
        allow_nan (bool, optional): Allow NaN and Infinity values. Defaults to True.
        default (Callable, optional): A callable that converts values that can not be encoded
            in to something that can be JSON encoded. Defaults to None.
        sort_keys (bool, optional): Sort dictionary keys. Defaults to False.
    """

    def __init__(
        self,
        json: str,
        indent: Union[None, int, str] = 2,
        highlight: bool = True,
        skip_keys: bool = False,
        ensure_ascii: bool = False,
        check_circular: bool = True,
        allow_nan: bool = True,
        default: Optional[Callable[[Any], Any]] = None,
        sort_keys: bool = False,
    ) -> None:
        data = _stdlib_json.loads(json)
        json = _stdlib_json.dumps(
            data,
            indent=indent,
            skipkeys=skip_keys,
            ensure_ascii=ensure_ascii,
            check_circular=check_circular,
            allow_nan=allow_nan,
            default=default,
            sort_keys=sort_keys,
        )
        from .highlighter import JSONHighlighter, NullHighlighter

        highlighter = JSONHighlighter() if highlight else NullHighlighter()
        self.text = highlighter(json)
        self.text.no_wrap = True
        self.text.overflow = None

    @classmethod
    def from_data(
        cls,
        data: Any,
        indent: Union[None, int, str] = 2,
        highlight: bool = True,
        skip_keys: bool = False,
        ensure_ascii: bool = False,
        check_circular: bool = True,
        allow_nan: bool = True,
        default: Optional[Callable[[Any], Any]] = None,
        sort_keys: bool = False,
    ) -> "JSON":
        """Encodes a JSON object from arbitrary data.

        Args:
            data (Any): An object that may be encoded in to JSON
            indent (Union[None, int, str], optional): Number of characters to indent by. Defaults to 2.
            highlight (bool, optional): Enable highlighting. Defaults to True.
            default (Callable, optional): Optional callable which will be called for objects that cannot be serialized. Defaults to None.
            skip_keys (bool, optional): Skip keys not of a basic type. Defaults to False.
            ensure_ascii (bool, optional): Escape all non-ascii characters. Defaults to False.
            check_circular (bool, optional): Check for circular references. Defaults to True.
            allow_nan (bool, optional): Allow NaN and Infinity values. Defaults to True.
            default (Callable, optional): A callable that converts values that can not be encoded
                in to something that can be JSON encoded. Defaults to None.
            sort_keys (bool, optional): Sort dictionary keys. Defaults to False.

        Returns:
            JSON: New JSON object from the given data.
        """
        json_instance: "JSON" = cls.__new__(cls)
        json = _stdlib_json.dumps(
            data,
            indent=indent,
            skipkeys=skip_keys,
            ensure_ascii=ensure_ascii,
            check_circular=check_circular,
            allow_nan=allow_nan,
            default=default,
            sort_keys=sort_keys,
        )
        from .highlighter import JSONHighlighter, NullHighlighter

        highlighter = JSONHighlighter() if highlight else NullHighlighter()
        json_instance.text = highlighter(json)
        json_instance.text.no_wrap = True
        json_instance.text.overflow = None
        return json_instance

    def __rich__(self) -> Any:
        return self.text

