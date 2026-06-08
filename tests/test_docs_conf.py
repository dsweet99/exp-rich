"""Ensure Sphinx configuration is part of the dependency graph."""


def test_docs_conf_project_name(monkeypatch):
    monkeypatch.setattr(
        "importlib.metadata.Distribution.from_name",
        lambda name: type("Distribution", (), {"version": "0.0.0"})(),
    )
    from docs.source.conf import project

    assert project == "Rich"
