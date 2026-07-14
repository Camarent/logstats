from pathlib import Path

import click

from core import main
from data import LogType


@click.command()
@click.argument(
    "filename", type=click.Path(exists=True, dir_okay=False, path_type=Path)
)
@click.option(
    "--level",
    type=click.Choice(LogType, case_sensitive=True),
    help="filter by this log level",
)
@click.option("--top", type=click.IntRange(min=1), help="show most common N messages")
@click.option("--per-hour", is_flag=True, help="show per hour messages counts")
def parse_aguments(
    filename: Path, level: LogType, top: int | None, per_hour: bool
) -> None:
    """Read a log file and print or filter its entries.

    FILENAME is the path to the log file to parse.
    """
    if top is not None and per_hour:
        raise click.UsageError(
            "--top and --per-hour can't be used together — pick one view."
        )

    main(filename, level, top, per_hour)


if __name__ == "__main__":
    parse_aguments()
