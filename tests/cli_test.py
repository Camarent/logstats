import json
import logging

import pytest
from click.testing import CliRunner

from logstats.cli import main


@pytest.fixture
def sample_log(tmp_path):
    log = tmp_path / "test.log"
    log.write_text("2026-07-13T09:22:10 ERROR Message")
    return log


def test_cli_doesnt_allow_multiple_reports(sample_log):
    result = CliRunner().invoke(main, [str(sample_log), "--top", "1", "--per-hour"])
    assert result.exit_code != 0
    assert "can't be used together" in result.output


def test_cli_no_logs_available(sample_log, caplog):
    with caplog.at_level(logging.INFO):
        result = CliRunner().invoke(main, [str(sample_log), "--level", "WARNING"])
    assert result.exit_code == 0
    assert "No logs" in caplog.text


def test_cli_end_to_end(sample_log):
    result = CliRunner().invoke(main, [str(sample_log), "--top", "1"])
    assert result.exit_code == 0
    assert "Message" in result.output


@pytest.mark.parametrize(
    "view", [[], ["--top", "1"], ["--per-hour"]], ids=["default", "top", "per-hour"]
)
def test_cli_json_output(sample_log, view: list[str]):
    result = CliRunner().invoke(main, [str(sample_log), "--json", *view])
    assert result.exit_code == 0
    reports = json.loads(result.stdout)
    assert isinstance(reports, list)
    assert len(reports) == 1
    assert set(reports[0]) == {"source", "header", "lines"}


def test_cli_json_no_logs_available(sample_log, caplog):
    with caplog.at_level(logging.INFO):
        result = CliRunner().invoke(
            main, [str(sample_log), "--json", "--level", "WARNING"]
        )
    assert result.exit_code == 0
    assert json.loads(result.stdout) == []
    assert "No logs" in caplog.text


def test_cli_json_no_sources(tmp_path, caplog):
    with caplog.at_level(logging.WARNING):
        result = CliRunner().invoke(main, [str(tmp_path / "missing.log"), "--json"])
    assert result.exit_code == 0
    assert json.loads(result.stdout) == []
    assert "failed to fetch" in caplog.text
