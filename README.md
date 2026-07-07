# logstats

A small, well-tested command-line tool that computes statistics from log files —
line counts, top-N error messages, requests-per-hour, and level filtering.

> **Status:** building in public over Week 1 of a Python foundation sprint.
> The point isn't the tool's novelty — it's clean, typed, tested Python with proper packaging and tooling.

## What it does (target)

```bash
logstats --file access.log --level ERROR --top 5
```

- Parse log lines into typed records
- Filter by level (`--level`)
- Top-N most frequent error messages (`--top`)
- Requests-per-hour buckets
- Readable, tested, `--help`-documented CLI

## Tech

Python 3.12+ · [`uv`](https://docs.astral.sh/uv/) · `click` · `pytest` · `ruff` · `mypy` (strict) · type hints & dataclasses throughout.

## Getting started (once built)

```bash
uv sync
uv run logstats --file sample.log --top 5
uv run pytest
```

## Roadmap (Week 1)

Tracked as issues under the **Week 1 — Python foundation** milestone:

- [ ] Day 1 — project setup + line count
- [ ] Day 2 — types & `LogEntry` dataclass + `--level` filter
- [ ] Day 3 — top-N errors (`Counter`) + requests/hour
- [ ] Day 4 — pytest suite + package structure
- [ ] Day 5 — `click` CLI + packaging + this README

## License

MIT — see [LICENSE](LICENSE).
