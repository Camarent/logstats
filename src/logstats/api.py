from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Annotated, cast

import httpx
from fastapi import APIRouter, FastAPI, HTTPException, Query, Request

from logstats.config import Settings, load_settings
from logstats.data import LogType
from logstats.schemas import TopResponse, gather_top_stats


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    app.state.settings = load_settings()
    app.state.client = httpx.AsyncClient()
    yield
    await app.state.client.aclose()


app = FastAPI(lifespan=lifespan)
router = APIRouter(prefix="/stats", tags=["stats"])
app.include_router(router)


def get_settings(request: Request) -> Settings:
    return cast(Settings, request.app.state.settings)


@router.get("/top")
async def get_top(
    request: Request,
    sources: Annotated[list[str], Query(min_length=1)],
    top: Annotated[int, Query(ge=1)] = 3,
    level: str | None = None,
    combined: bool = False,
) -> TopResponse:
    settings = get_settings(request)
    try:
        urls = {name: settings.get_source_url(name) for name in sources}
    except KeyError as exc:
        raise HTTPException(422, f"Unknown source: {exc.args[0]}")

    try:
        parsed = LogType[level.upper()] if level else None
    except (KeyError, ValueError) as exc:
        raise HTTPException(422, f"Unknown level: {exc.args[0]}")

    return await gather_top_stats(urls, parsed, top, combined, request.app.state.client)
