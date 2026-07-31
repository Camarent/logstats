from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Annotated, cast

import httpx
from fastapi import APIRouter, Depends, FastAPI, HTTPException, Query, Request
from fastapi.responses import StreamingResponse

from logstats.config import Settings, load_settings
from logstats.data import LogType
from logstats.fetcher import TIMEOUT
from logstats.schemas import (
    PerHourResponse,
    TopResponse,
    gather_per_hour_stats,
    gather_top_stats,
    stream_all,
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    app.state.settings = load_settings()
    app.state.client = httpx.AsyncClient(timeout=TIMEOUT)
    yield
    await app.state.client.aclose()


app = FastAPI(lifespan=lifespan)
router = APIRouter(prefix="/stats", tags=["stats"])


def get_settings(request: Request) -> Settings:
    return cast(Settings, request.app.state.settings)


def get_client(request: Request) -> httpx.AsyncClient:
    return cast(httpx.AsyncClient, request.app.state.client)


def get_urls(
    sources: Annotated[list[str], Query(min_length=1)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> dict[str, str]:
    try:
        urls = {name: settings.get_source_url(name) for name in sources}
    except KeyError as exc:
        raise HTTPException(422, f"Unknown source: {exc.args[0]}")
    return urls


def parse_level(level: str | None = None) -> LogType | None:
    try:
        parsed = LogType[level.upper()] if level else None
    except (KeyError, ValueError) as exc:
        raise HTTPException(422, f"Unknown level: {exc.args[0]}")
    return parsed


@router.get("/top")
async def get_top(
    urls: Annotated[dict[str, str], Depends(get_urls)],
    client: Annotated[httpx.AsyncClient, Depends(get_client)],
    level: Annotated[LogType | None, Depends(parse_level)],
    top: Annotated[int, Query(ge=1)] = 3,
    combined: bool = False,
) -> TopResponse:
    return await gather_top_stats(urls, level, top, combined, client)


@router.get("/per-hour")
async def get_per_hour(
    urls: Annotated[dict[str, str], Depends(get_urls)],
    client: Annotated[httpx.AsyncClient, Depends(get_client)],
    level: Annotated[LogType | None, Depends(parse_level)],
    combined: bool = False,
) -> PerHourResponse:
    return await gather_per_hour_stats(urls, level, combined, client)


@router.get("/regular")
async def get_regular(
    urls: Annotated[dict[str, str], Depends(get_urls)],
    client: Annotated[httpx.AsyncClient, Depends(get_client)],
    level: Annotated[LogType | None, Depends(parse_level)],
) -> StreamingResponse:
    return StreamingResponse(
        stream_all(urls, level, client), media_type="text/event-stream"
    )


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(router)
