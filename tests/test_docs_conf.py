def test_sphinx_conf_integrated() -> None:
    from docs.source import conf

    assert conf.project == "Rich"
