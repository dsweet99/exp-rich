from __future__ import annotations

from typing import Any, Iterable, Tuple, Union

Result = Iterable[Union[Any, Tuple[Any], Tuple[str, Any], Tuple[str, Any, Any]]]
RichReprResult = Result
