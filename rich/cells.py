from __future__ import annotations

from functools import lru_cache
from operator import itemgetter
from typing import Callable, Sequence, Tuple

from rich._cell_table import CellTable
from rich._unicode_data import load as load_cell_table

CellSpan = Tuple[int, int, int]

_span_get_cell_len = itemgetter(2)

# Ranges of unicode ordinals that produce a 1-cell wide character
# This is non-exhaustive, but covers most common Western characters
_SINGLE_CELL_UNICODE_RANGES: list[tuple[int, int]] = [
    (0x20, 0x7E),  # Latin (excluding non-printable)
    (0xA0, 0xAC),
    (0xAE, 0x002FF),
    (0x00370, 0x00482),  # Greek / Cyrillic
    (0x02500, 0x025FC),  # Box drawing, box elements, geometric shapes
    (0x02800, 0x028FF),  # Braille
]

# A frozen set of characters that are a single cell wide
_SINGLE_CELLS = frozenset(
    [
        character
        for _start, _end in _SINGLE_CELL_UNICODE_RANGES
        for character in map(chr, range(_start, _end + 1))
    ]
)

# When called with a string this will return True if all
# characters are single-cell, otherwise False
_is_single_cell_widths: Callable[[str], bool] = _SINGLE_CELLS.issuperset


@lru_cache(maxsize=4096)
def get_character_cell_size(character: str, unicode_version: str = "auto") -> int:
    """Get the cell size of a character.

    Args:
        character (str): A single character.
        unicode_version: Unicode version, `"auto"` to auto detect, `"latest"` for the latest unicode version.

    Returns:
        int: Number of cells (0, 1 or 2) occupied by that character.
    """
    codepoint = ord(character)
    if codepoint and codepoint < 32 or 0x07F <= codepoint < 0x0A0:
        return 0
    table = load_cell_table(unicode_version).widths

    last_entry = table[-1]
    if codepoint > last_entry[1]:
        return 1

    lower_bound = 0
    upper_bound = len(table) - 1

    while lower_bound <= upper_bound:
        index = (lower_bound + upper_bound) >> 1
        start, end, width = table[index]
        if codepoint < start:
            upper_bound = index - 1
        elif codepoint > end:
            lower_bound = index + 1
        else:
            return width
    return 1


@lru_cache(4096)
def cached_cell_len(text: str, unicode_version: str = "auto") -> int:
    """Get the number of cells required to display text.

    This method always caches, which may use up a lot of memory. It is recommended to use
    `cell_len` over this method.

    Args:
        text (str): Text to display.
        unicode_version: Unicode version, `"auto"` to auto detect, `"latest"` for the latest unicode version.

    Returns:
        int: Get the number of cells required to display text.
    """
    return _cell_len(text, unicode_version)


def cell_len(text: str, unicode_version: str = "auto") -> int:
    """Get the cell length of a string (length as it appears in the terminal).

    Args:
        text: String to measure.
        unicode_version: Unicode version, `"auto"` to auto detect, `"latest"` for the latest unicode version.

    Returns:
        Length of string in terminal cells.
    """
    if len(text) < 512:
        return cached_cell_len(text, unicode_version)
    return _cell_len(text, unicode_version)


def _cell_len_special_char(
    character: str,
    unicode_version: str,
    last_measured_character: str | None,
    total_width: int,
    cell_table: CellTable,
) -> tuple[str | None, int]:
    if character_width := get_character_cell_size(character, unicode_version):
        return character, total_width + character_width
    return last_measured_character, total_width


def _cell_len_special_zwj(index: int) -> int:
    return index + 1


def _cell_len_special_fe0f(
    last_measured_character: str | None,
    total_width: int,
    cell_table: CellTable,
) -> tuple[str | None, int]:
    if not last_measured_character:
        return last_measured_character, total_width
    total_width += last_measured_character in cell_table.narrow_to_wide
    return None, total_width


def _cell_len_special_step(
    character: str,
    index: int,
    last_measured_character: str | None,
    total_width: int,
    unicode_version: str,
    cell_table: CellTable,
    special: set[str],
) -> tuple[int, str | None, int]:
    if character not in special:
        return (
            index,
            *_cell_len_special_char(
                character, unicode_version, last_measured_character, total_width, cell_table
            ),
        )
    if character == "\u200d":
        return _cell_len_special_zwj(index), last_measured_character, total_width
    return index, *_cell_len_special_fe0f(
        last_measured_character, total_width, cell_table
    )


def _cell_len_special(
    text: str,
    unicode_version: str,
    cell_table: CellTable,
) -> int:
    total_width = 0
    last_measured_character: str | None = None
    special = {"\u200d", "\ufe0f"}
    index = 0
    character_count = len(text)
    while index < character_count:
        character = text[index]
        index, last_measured_character, total_width = _cell_len_special_step(
            character,
            index,
            last_measured_character,
            total_width,
            unicode_version,
            cell_table,
            special,
        )
        index += 1
    return total_width


def _cell_len(text: str, unicode_version: str) -> int:
    """Get the cell length of a string (length as it appears in the terminal).

    Args:
        text: String to measure.
        unicode_version: Unicode version, `"auto"` to auto detect, `"latest"` for the latest unicode version.

    Returns:
        Length of string in terminal cells.
    """

    if _is_single_cell_widths(text):
        return len(text)

    # "\u200d" is zero width joiner
    # "\ufe0f" is variation selector 16
    if "\u200d" not in text and "\ufe0f" not in text:
        # Simplest case with no unicode stuff that changes the size
        return sum(
            get_character_cell_size(character, unicode_version) for character in text
        )

    cell_table = load_cell_table(unicode_version)
    return _cell_len_special(text, unicode_version, cell_table)


def _extend_zero_width_grapheme(
    spans: list[tuple[int, int, int]], index: int
) -> int:
    if spans:
        start, _end, cell_length = spans[-1]
        spans[-1] = (start, index := index + 1, cell_length)
        return index
    spans.append((index, index := index + 1, 0))
    return index


def _split_special_grapheme(
    character: str,
    index: int,
    codepoint_count: int,
    spans: list[tuple[int, int, int]],
    cell_table: CellTable,
    last_measured_character: str | None,
    total_width: int,
) -> tuple[int, str | None, int]:
    if not spans:
        spans.append((index, index := index + 1, 0))
        return index, last_measured_character, total_width
    if character == "\u200d":
        index += 2 if index < (codepoint_count - 1) else 1
        start, _end, cell_length = spans[-1]
        spans[-1] = (start, index, cell_length)
        return index, last_measured_character, total_width
    index += 1
    if last_measured_character:
        start, _end, cell_length = spans[-1]
        if last_measured_character in cell_table.narrow_to_wide:
            last_measured_character = None
            cell_length += 1
            total_width += 1
        spans[-1] = (start, index, cell_length)
    else:
        start, _end, cell_length = spans[-1]
        spans[-1] = (start, index, cell_length)
    return index, last_measured_character, total_width


def split_graphemes(
    text: str, unicode_version: str = "auto"
) -> "tuple[list[CellSpan], int]":
    """Divide text into spans that define a single grapheme, and additionally return the cell length of the whole string.

    The returned spans will cover every index in the string, with no gaps. It is possible for some graphemes to have a cell length of zero.
    This can occur for nonsense strings like two zero width joiners, or for control codes that don't contribute to the grapheme size.

    Args:
        text: String to split.
        unicode_version: Unicode version, `"auto"` to auto detect, `"latest"` for the latest unicode version.

    Returns:
        A tuple of a list of *spans* and the cell length of the entire string. A span is a list of tuples
            of three values consisting of (<START>, <END>, <CELL LENGTH>), where START and END are string indices,
            and CELL LENGTH is the cell length of the single grapheme.
    """

    cell_table = load_cell_table(unicode_version)
    codepoint_count = len(text)
    index = 0
    last_measured_character: str | None = None

    total_width = 0
    spans: list[tuple[int, int, int]] = []
    SPECIAL = {"\u200d", "\ufe0f"}
    while index < codepoint_count:
        if (character := text[index]) in SPECIAL:
            index, last_measured_character, total_width = _split_special_grapheme(
                character,
                index,
                codepoint_count,
                spans,
                cell_table,
                last_measured_character,
                total_width,
            )
            continue

        if character_width := get_character_cell_size(character, unicode_version):
            last_measured_character = character
            spans.append((index, index := index + 1, character_width))
            total_width += character_width
        else:
            index = _extend_zero_width_grapheme(spans, index)

    return (spans, total_width)


def _split_text_at_offset(
    text: str,
    spans: list[tuple[int, int, int]],
    offset: int,
    left_size: int,
    cell_position: int,
) -> tuple[str, str] | tuple[int, int] | None:
    if left_size == cell_position:
        if offset >= len(spans):
            return text, ""
        split_index = spans[offset][0]
        return text[:split_index], text[split_index:]
    if left_size < cell_position:
        start, end, cell_size = spans[offset]
        if left_size + cell_size > cell_position:
            return text[:start] + " ", " " + text[end:]
        return offset + 1, left_size + cell_size
    start, end, cell_size = spans[offset - 1]
    if left_size - cell_size < cell_position:
        return text[:start] + " ", " " + text[end:]
    return offset - 1, left_size - cell_size


def _split_text(
    text: str, cell_position: int, unicode_version: str = "auto"
) -> tuple[str, str]:
    """Split text by cell position.

    If the cell position falls within a double width character, it is converted to two spaces.

    Args:
        text: Text to split.
        cell_position Offset in cells.
        unicode_version: Unicode version, `"auto"` to auto detect, `"latest"` for the latest unicode version.

    Returns:
        Tuple to two split strings.
    """
    if cell_position <= 0:
        return "", text

    spans, cell_length = split_graphemes(text, unicode_version)

    # Guess initial offset
    offset = int((cell_position / cell_length) * len(spans))
    left_size = sum(map(_span_get_cell_len, spans[:offset]))

    while True:
        result = _split_text_at_offset(
            text, spans, offset, left_size, cell_position
        )
        if isinstance(result, tuple) and isinstance(result[0], str):
            return result
        offset, left_size = result


def split_text(
    text: str, cell_position: int, unicode_version: str = "auto"
) -> tuple[str, str]:
    """Split text by cell position.

    If the cell position falls within a double width character, it is converted to two spaces.

    Args:
        text: Text to split.
        cell_position Offset in cells.
        unicode_version: Unicode version, `"auto"` to auto detect, `"latest"` for the latest unicode version.

    Returns:
        Tuple to two split strings.
    """
    if _is_single_cell_widths(text):
        return text[:cell_position], text[cell_position:]
    return _split_text(text, cell_position, unicode_version)


def set_cell_size(text: str, total: int, unicode_version: str = "auto") -> str:
    """Adjust a string by cropping or padding with spaces such that it fits within the given number of cells.

    Args:
        text: String to adjust.
        total: Desired size in cells.
        unicode_version: Unicode version.

    Returns:
        A string with cell size equal to total.
    """
    if _is_single_cell_widths(text):
        size = len(text)
        if size < total:
            return text + " " * (total - size)
        return text[:total]
    if total <= 0:
        return ""
    cell_size = cell_len(text)
    if cell_size == total:
        return text
    if cell_size < total:
        return text + " " * (total - cell_size)
    text, _ = _split_text(text, total, unicode_version)
    return text


def chop_cells(text: str, width: int, unicode_version: str = "auto") -> list[str]:
    """Split text into lines such that each line fits within the available (cell) width.

    Args:
        text: The text to fold such that it fits in the given width.
        width: The width available (number of cells).

    Returns:
        A list of strings such that each string in the list has cell width
        less than or equal to the available width.
    """
    if _is_single_cell_widths(text):
        return [text[index : index + width] for index in range(0, len(text), width)]
    spans, _ = split_graphemes(text, unicode_version)
    line_size = 0  # Size of line in cells
    lines: list[str] = []
    line_offset = 0  # Offset (in codepoints) of start of line
    for start, end, cell_size in spans:
        if line_size + cell_size > width:
            lines.append(text[line_offset:start])
            line_offset = start
            line_size = 0
        line_size += cell_size
    if line_size:
        lines.append(text[line_offset:])

    return lines
