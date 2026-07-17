from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path


class InvalidLogFormat(Exception):
    pass


class LogType(Enum):
    DEBUG = 0
    INFO = 1
    WARNING = 2
    ERROR = 3


def get_name_capitalize(level: LogType | None) -> str:
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
            raise InvalidLogFormat(f"Log line has invalid format: {self.log_line}")

        self.timestamp = datetime.fromisoformat(log_split[0])
        self.level = LogType[log_split[1]]
        self.message = log_split[2]

    def __str__(self) -> str:
        return f"[{self.timestamp}] {self.level.name}: {self.message}"


@dataclass(frozen=True)
class Query:
    filename: Path
    level: LogType | None
    top: int | None
    per_hour: bool
