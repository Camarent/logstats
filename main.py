from dataclasses import dataclass, field
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
    text: str
    char_count: int = field(init=False)
    log_type: LogType = field(init=False)

    def __post_init__(self):
        self.char_count = len(self.text)
        self.log_type = next((lt for lt in LogType if lt.name in self.text), None)


def file_len(filename: Path) -> int:
    with filename.open("rb") as f:
        num_lines = sum(1 for _ in f)
        return num_lines


def parse_file(filename: Path, filter: LogType) -> list[LogEntry]:
    logs = []
    with filename.open("rt") as f:
        for line in f:
            parsed_line = parse(line)
            if filter is None or parsed_line.log_type == filter:
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
def main(filename, level: LogType):
    logs = parse_file(Path(filename), level)
    print("File line count is", len(logs))


if __name__ == "__main__":
    main()
