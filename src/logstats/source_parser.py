import logging
from collections.abc import AsyncIterator
from dataclasses import dataclass
from enum import Enum, auto
from urllib.parse import urlparse

import aiofiles
import httpx

from logstats.data import InvalidLogFormat, LogEntry, LogType

logger = logging.getLogger(__name__)


class SourceType(Enum):
    UNKNOWN = auto()
    PATH = auto()
    HTTP_S = auto()


@dataclass
class FetchedSource:
    log_lines: list[LogEntry]
    source: str
    error: str | None = None


async def fetch_source(
    source: str, level: LogType | None, client: httpx.AsyncClient
) -> FetchedSource:
    try:
        lines = [e async for e in stream_entries(source, level, client)]
        return FetchedSource(lines, source)
    except (httpx.HTTPError, OSError) as exc:
        logger.warning(f"failed to fetch {source}: {exc}")
        return FetchedSource([], source, error=str(exc))


def get_source_type(source: str) -> SourceType:
    scheme = urlparse(source).scheme
    if scheme in ("http", "https"):
        return SourceType.HTTP_S
    if scheme == "":
        return SourceType.PATH
    return SourceType.UNKNOWN


async def stream_entries(
    source: str, level: LogType | None, client: httpx.AsyncClient
) -> AsyncIterator[LogEntry]:
    async for line in stream_lines(source, client):
        entry = parse_line(line, level)
        if entry is not None:
            yield entry


async def stream_lines(source: str, client: httpx.AsyncClient) -> AsyncIterator[str]:
    match get_source_type(source):
        case SourceType.HTTP_S:
            async with client.stream("GET", source) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    yield line
        case SourceType.PATH:
            async with aiofiles.open(source) as f:
                async for line in f:
                    yield line
        case _:
            return


def parse_line(line: str, level: LogType | None) -> LogEntry | None:
    try:
        entry = LogEntry(line.rstrip("\n"))
        return entry if level is None or entry.level == level else None
    except InvalidLogFormat as ex:
        logger.warning(ex)
    except (ValueError, KeyError) as gex:
        logger.warning(f'Exception "{gex}" was raised for line "{line}"')
    return None
