import asyncio
import logging
from collections.abc import Sequence

from logstats.data import LogType, ReportRequest
from logstats.parser import fetch
from logstats.report import create_reports

logger = logging.getLogger(__name__)


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
