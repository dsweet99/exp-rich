"""Tests for examples.table_movie."""
from __future__ import annotations

import examples.table_movie as table_movie_module


def test_beat_context_manager(monkeypatch):
    monkeypatch.setattr(f"{table_movie_module.__name__}.time.sleep", lambda *_: None)
    with table_movie_module.beat(1):
        pass
