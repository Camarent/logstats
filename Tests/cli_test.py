from click.testing import CliRunner

from logstats.cli import parse_aguments


def test_cli_doesnt_allow_multiple_reports(tmp_path):
    log = tmp_path / "test.log"
    log.write_text("2026-07-13T09:22:10 ERROR Message")
    result = CliRunner().invoke(parse_aguments, [str(log), "--top", "1", "--per-hour"])
    assert result.exit_code != 0
    assert "can't be used together" in result.output


def test_cli_end_to_end(tmp_path):
    log = tmp_path / "test.log"
    log.write_text("2026-07-13T09:22:10 ERROR Message")
    result = CliRunner().invoke(parse_aguments, [str(log), "--top", "1"])
    assert result.exit_code == 0
    assert "Message" in result.output
