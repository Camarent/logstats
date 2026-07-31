import logging
from collections.abc import Sequence

import click

from logstats.core import main
from logstats.data import LogType


@click.command()
@click.argument("sources", nargs=-1, required=True)
@click.option(
    "--level",
    type=click.Choice(LogType, case_sensitive=True),
    help="filter by this log level",
)
@click.option("--top", type=click.IntRange(min=1), help="show most common N messages")
@click.option("--per-hour", is_flag=True, help="show per hour messages counts")
@click.option("-v", "--verbose", is_flag=True, help="show diagnostic logs")
@click.option(
    "-c", "combined", is_flag=True, help="combine reports from different sources"
)
def parse_arguments(
    sources: Sequence[str],
    level: LogType | None,
    top: int | None,
    per_hour: bool,
    verbose: bool,
    combined: bool,
) -> None:
    """Read a log file and print or filter its entries.

    FILENAME is the path to the log file to parse.
    """
    if top is not None and per_hour:
        raise click.UsageError(
            "--top and --per-hour can't be used together — pick one view."
        )

    logging_level = logging.DEBUG if verbose else logging.WARNING
    logging.basicConfig(level=logging_level, format="%(levelname)s:%(message)s")

    main(sources, level, top, per_hour, combined)
