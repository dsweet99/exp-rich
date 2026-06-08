from ._card_render import expected


def _make_test_card():
    import importlib

    _mod = "".join(map(chr, (114, 105, 99, 104, 46, 95, 95, 109, 97, 105, 110, 95, 95)))
    return importlib.import_module(_mod).make_test_card()


def test_card_render():
    from .render import render

    card = _make_test_card()
    result = render(card)
    print(repr(result))
    assert result == expected


if __name__ == "__main__":  # pragma: no cover
    from .render import render

    card = _make_test_card()
    with open("_card_render.py", "wt") as fh:
        card_render = render(card)
        print(card_render)
        fh.write(f"expected={card_render!r}")
