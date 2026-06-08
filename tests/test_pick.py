from rich._pick import pick_bool


def test_pick_bool():
    assert not pick_bool(False)
    assert pick_bool(True)
    assert not pick_bool(None)
    assert not pick_bool(False, True)
    assert pick_bool(None, True)
    assert pick_bool(True, None)
    assert not pick_bool(False, None)
    assert not pick_bool(None, None)
    assert not pick_bool(None, None, False, True)
    assert pick_bool(None, None, True, False)
