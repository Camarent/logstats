import asyncio
import json
import logging
from collections.abc import Sequence
from functools import partial

from logstats.data import LogType, ReportRequest
from logstats.fetcher import fetch
from logstats.per_hour_stats import compute_per_hour
from logstats.report import Report, format_hourly, format_regular, format_top
from logstats.source_parser import FetchedSource
from logstats.stats import build_stats, merge_entries
from logstats.top_stats import compute_top

logger = logging.getLogger(__name__)


def create_reports(
    sources: Sequence[FetchedSource], request: ReportRequest
) -> list[Report]:
    if request.top is not None:
        tops = build_stats(
            sources,
            request.combined_report,
            partial(compute_top, level=request.level, top=request.top),
        )
        return [format_top(st) for st in tops]
    elif request.per_hour:
        hourly = build_stats(
            sources,
            request.combined_report,
            partial(compute_per_hour, level=request.level),
        )
        return [format_hourly(st) for st in hourly]
    else:
        return [format_regular(merge_entries(sources))]


def main(
    sources: Sequence[str],
    level: LogType | None,
    top: int | None,
    per_hour: bool,
    combined: bool,
    as_json: bool = False,
) -> None:
    request = ReportRequest(level, top, per_hour, combined)
    fetched_sources = asyncio.run(fetch(sources, request.level))
    reports: list[Report] = []
    if len(fetched_sources) == 0:
        logger.warning("No available sources.")
    elif all(not fs.entries for fs in fetched_sources):
        logger.info("No logs available with the selected filters.")
    else:
        reports = create_reports(fetched_sources, request)
    if as_json:
        print(json.dumps([r.to_dict() for r in reports]))
        return
    for report in reports:
        print(report)
