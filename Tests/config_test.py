import tomllib
from pathlib import Path

import pytest
from pydantic import ValidationError

from logstats.config import DEFAULT_SOURCES, load_settings, resolve_sources_path


def write_toml(tmp_path, content: str):
    path = tmp_path / "sources.toml"
    path.write_text(content)
    return path


def test_relative_path_becomes_absolute(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert resolve_sources_path(Path("custom.toml")) == tmp_path / "custom.toml"


def test_falls_back_to_default_name_without_env_var(tmp_path, monkeypatch):
    monkeypatch.delenv("LOGSTATS_SOURCES", raising=False)
    monkeypatch.chdir(tmp_path)
    assert resolve_sources_path() == tmp_path / DEFAULT_SOURCES


def test_symlinks_are_not_followed(tmp_path):
    target = write_toml(tmp_path, '[sources]\napp1 = "sample.log"\n')
    link = tmp_path / "link.toml"
    link.symlink_to(target)
    assert resolve_sources_path(link) == link


def test_loads_named_sources(tmp_path):
    path = write_toml(tmp_path, '[sources]\napp1 = "http://logs.test/app1.log"\n')
    settings = load_settings(path)
    assert settings.sources == {"app1": "http://logs.test/app1.log"}


def test_path_defaults_to_env_var(tmp_path, monkeypatch):
    path = write_toml(tmp_path, '[sources]\napp1 = "sample.log"\n')
    monkeypatch.setenv("LOGSTATS_SOURCES", str(path))
    assert load_settings().sources == {"app1": "sample.log"}


@pytest.mark.parametrize(
    "content, expected_error",
    [
        ('name = "logstats"\n', ValidationError),
        ('sources = "not-a-table"\n', ValidationError),
        ("[sources]\napp1 = 42\n", ValidationError),
        ("[sources\napp1 = broken", tomllib.TOMLDecodeError),
    ],
    ids=["missing-table", "sources-not-a-table", "url-not-a-string", "malformed-toml"],
)
def test_invalid_config_is_rejected(tmp_path, content, expected_error):
    path = write_toml(tmp_path, content)
    with pytest.raises(expected_error):
        load_settings(path)
