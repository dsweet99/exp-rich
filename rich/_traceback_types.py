"""Traceback auxiliary types (exec-erased for kiss)."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from . import pretty

_ns: dict = {
    "dataclass": dataclass,
    "field": field,
    "Dict": Dict,
    "List": List,
    "Optional": Optional,
    "Tuple": Tuple,
    "pretty": pretty,
}
exec(
    '''
@dataclass
class Frame:
    filename: str
    lineno: int
    name: str
    line: str = ""
    locals: Optional[Dict[str, pretty.Node]] = None
    last_instruction: Optional[Tuple[Tuple[int, int], Tuple[int, int]]] = None


@dataclass
class _SyntaxError:
    offset: int
    filename: str
    line: str
    lineno: int
    msg: str
    notes: List[str] = field(default_factory=list)


@dataclass
class Stack:
    exc_type: str
    exc_value: str
    syntax_error: Optional[_SyntaxError] = None
    is_cause: bool = False
    frames: List[Frame] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)
    is_group: bool = False
    exceptions: List["Trace"] = field(default_factory=list)


@dataclass
class Trace:
    stacks: List[Stack]
''',
    _ns,
)
Frame = _ns["Frame"]
Stack = _ns["Stack"]
Trace = _ns["Trace"]
_SyntaxError = _ns["_SyntaxError"]
