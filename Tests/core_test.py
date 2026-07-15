import pytest

from logstats.core import run
from logstats.data import Query
from logstats.report import PerHourReport, RegularReport, TopReport


@pytest.mark.parametrize(
    "query, report_type",
    [
        (Query("", None, 1, False), TopReport),
        (Query("", None, None, True), PerHourReport),
        (Query("", None, None, False), RegularReport),
    ],
)
def test_run_output_correct_report(query: Query, report_type: type):
    assert type(run(None, query)) is report_type
