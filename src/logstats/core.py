import asyncio
import logging
from collections.abc import Sequence
from functools import partial

from logstats.data import LogType, ReportRequest
from logstats.parser import fetch
from logstats.per_hour_stats import compute_per_hour
from logstats.report import (
    PerHourReportFormatted,
    RegularReportFormatted,
    ReportFormatted,
    TopReportFormatted,
)
from logstats.source_parser import FetchedSource
from logstats.stats import build_stats, merge_entries
from logstats.top_stats import compute_top

logger = logging.getLogger(__name__)


def create_reports(
    sources: Sequence[FetchedSource], request: ReportRequest
) -> list[ReportFormatted]:
    if request.top is not None:
        tops = build_stats(
            sources,
            request.combined_report,
            partial(compute_top, level=request.level, top=request.top),
        )
        return [TopReportFormatted(st) for st in tops]
    elif request.per_hour:
        hourly = build_stats(
            sources,
            request.combined_report,
            partial(compute_per_hour, level=request.level),
        )
        return [PerHourReportFormatted(st) for st in hourly]
    else:
        return [RegularReportFormatted(merge_entries(sources))]


def main(
    sources: Sequence[str],
    level: LogType | None,
    top: int | None,
    per_hour: bool,
    combined: bool,
) -> None:
    request = ReportRequest(level, top, per_hour, combined)
    fetched_sources = asyncio.run(fetch(sources, request.level))
    if len(fetched_sources) == 0:
        logger.warning("No available sources.")
        return
    if all(not fs.log_lines for fs in fetched_sources):
        logger.info("No logs available with the selected filters.")
        return
    for report in create_reports(fetched_sources, request):
        print(report)
