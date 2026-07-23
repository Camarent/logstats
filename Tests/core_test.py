from pathlib import Path

import pytest

from logstats.core import run
from logstats.data import Query
from logstats.report import PerHourReport, RegularReport, TopReport


@pytest.mark.parametrize(
    "query, report_type",
    [
        (Query(Path(""), None, 1, False), TopReport),
        (Query(Path(""), None, None, True), PerHourReport),
        (Query(Path(""), None, None, False), RegularReport),
    ],
)
def test_run_output_correct_report(query: Query, report_type: type):
    assert type(run([], query)) is report_type
