from typing import Tuple, Union

PaddingDimensions = Union[int, Tuple[int], Tuple[int, int], Tuple[int, int, int, int]]


def unpack_padding(pad: PaddingDimensions) -> Tuple[int, int, int, int]:
    """Unpack padding specified in CSS style."""
    if isinstance(pad, int):
        return (pad, pad, pad, pad)
    if len(pad) == 1:
        _pad = pad[0]
        return (_pad, _pad, _pad, _pad)
    if len(pad) == 2:
        pad_top, pad_right = pad
        return (pad_top, pad_right, pad_top, pad_right)
    if len(pad) == 4:
        top, right, bottom, left = pad
        return (top, right, bottom, left)
    raise ValueError(f"1, 2 or 4 integers required for padding; {len(pad)} given")
