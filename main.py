from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path

import click


class InvalidFormat(Exception):
    pass


class LogType(Enum):
    DEBUG = 0
    INFO = 1
    WARNING = 2
    ERROR = 3


def get_name_capitalize(level: LogType) -> str:
    return level.name.capitalize() if level else "All"


@dataclass
class LogEntry:
    log_line: str
    message: str = field(init=False)
    level: LogType = field(init=False)
    timestamp: datetime = field(init=False)

    def __post_init__(self) -> None:
        log_split = self.log_line.split(maxsplit=2)
        if len(log_split) != 3:
            raise InvalidFormat(f"Log line has invalid format: {self.log_line}")

        self.timestamp = datetime.fromisoformat(log_split[0])
        self.level = LogType[log_split[1]]
        self.message = log_split[2].rstrip("\n")

    def __str__(self) -> str:
        return f"[{self.timestamp}] {self.level.name}: {self.message}"


def file_len(filename: Path) -> int:
    with filename.open("rb") as f:
        num_lines = sum(1 for _ in f)
        return num_lines


def parse_file(filename: Path, filter: LogType) -> list[LogEntry]:
    logs = []
    with filename.open("rt") as f:
        for line in f:
            parsed_line = parse(line)
            if parsed_line is not None and (
                filter is None or parsed_line.level == filter
            ):
                logs.append(parsed_line)
        return logs


def parse(line: str) -> LogEntry | None:
    try:
        return LogEntry(line)
    except InvalidFormat as ex:
        print(ex)
    except (ValueError, KeyError) as gex:
        print(f'Exception "{gex}" was raised for line "{line}"')


def top_output(logs: list[LogEntry], top: int, level: LogType) -> None:
    messages = Counter((e.level, e.message) for e in logs)
    scope = get_name_capitalize(level)
    print(f"Top {top} {scope} messages:")
    for (lvl, msg), n in messages.most_common(top):
        print(f"    {n} x {lvl.name.capitalize()}: {msg}")


def per_hour_output(logs: list[LogEntry], level: LogType) -> None:
    messages = Counter((e.timestamp.date(), e.timestamp.hour) for e in logs)
    scope = get_name_capitalize(level)
    print(f"{scope} messages per hour:")
    for (day, hour), n in sorted(messages.items()):
        print(f"    {day} {hour:02d}:00     {n}")


def regular_output(logs: list[LogEntry]) -> None:
    for lt in logs:
        print(lt)


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
def main(filename: Path, level: LogType, top: int | None, per_hour: bool) -> None:
    """Read a log file and print or filter its entries.

    FILENAME is the path to the log file to parse.
    """
    if top is not None and per_hour:
        raise click.UsageError(
            "--top and --per-hour can't be used together — pick one view."
        )

    logs = parse_file(filename, level)
    if len(logs) == 0:
        print("No logs avaiable with the selected filters.")
        return

    if top is not None:
        top_output(logs, top, level)
    elif per_hour:
        per_hour_output(logs, level)
    else:
        regular_output(logs)


if __name__ == "__main__":
    main()
