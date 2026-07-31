import os
import tomllib
from pathlib import Path

from pydantic import BaseModel


class Settings(BaseModel):
    sources: dict[str, str]

    def get_source_url(self, name: str) -> str:
        return self.sources[name]


DEFAULT_SOURCES = "sources.toml"


def resolve_sources_path(path: Path | None = None) -> Path:
    """Return the sources config as an absolute path, without following symlinks.

    Falls back to $LOGSTATS_SOURCES, then to sources.toml in the working directory.
    """
    if path is None:
        path = Path(os.environ.get("LOGSTATS_SOURCES", DEFAULT_SOURCES))
    return path.absolute()


def load_settings(path: Path | None = None) -> Settings:
    resolved = resolve_sources_path(path)
    with resolved.open("rb") as f:
        return Settings(**tomllib.load(f))
