import os
import tomllib
from pathlib import Path

from pydantic import BaseModel


class Settings(BaseModel):
    sources: dict[str, str]

    def get_source_url(self, name: str) -> str:
        return self.sources[name]


def load_settings(path: Path | None = None) -> Settings:
    if path is None:
        path = Path(os.environ.get("LOGSTATS_SOURCES", "sources.toml"))
    with path.open("rb") as f:
        return Settings(**tomllib.load(f))
