import logstats

EXPECTED = ["stream_lines", "parse_line", "compute_top", "compute_per_hour"]


def test_public_api_exports_all_names():
    assert sorted(logstats.__all__) == sorted(EXPECTED)


def test_public_api_names_are_importable():
    for name in EXPECTED:
        assert callable(getattr(logstats, name)), name
