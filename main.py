from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path

import click


class LogType(Enum):
    DEBUG = 0
    INFO = 1
    WARNING = 2
    ERROR = 3


@dataclass
class LogEntry:
    log_line: str
    message: str = field(init=False)
    level: LogType = field(init=False)
    timestamp: datetime = field(init=False)

    def __post_init__(self) -> None:
        log_split = self.log_line.split(maxsplit=2)
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
            if filter is None or parsed_line.level == filter:
                logs.append(parsed_line)
        return logs


def parse(line: str) -> LogEntry:
    return LogEntry(line)


@click.command()
@click.argument("filename")
@click.option(
    "--level",
    type=click.Choice(LogType, case_sensitive=True),
    help="filter by this log level",
)
def main(filename: str, level: LogType) -> None:
    logs = parse_file(Path(filename), level)
    for lt in logs:
        print(lt)


if __name__ == "__main__":
    main()
