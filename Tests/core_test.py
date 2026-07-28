import logging

from logstats.core import main


def test_no_source_fetched(monkeypatch, caplog):
    async def fake_fetch(sources, level):
        return []

    monkeypatch.setattr("logstats.core.fetch", fake_fetch)
    with caplog.at_level(logging.WARNING):
        main(["test.log"], None, None, False, False)
    assert "No available sources" in caplog.text
