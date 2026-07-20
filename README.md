# logstats

[![CI](https://github.com/Camarent/logstats/actions/workflows/code_quality_check.yml/badge.svg)](https://github.com/Camarent/logstats/actions/workflows/code_quality_check.yml)
[![coverage](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/Camarent/6d7c1f051b41f3084116ccc594267742/raw/logstats-coverage.json)](https://github.com/Camarent/logstats/actions/workflows/code_quality_check.yml)

A small, well-tested command-line tool that computes statistics from log files —
line counts, top-N error messages, requests-per-hour, and level filtering.

> **Status:** built in public over Week 1 of a Python foundation sprint.
> The point isn't the tool's novelty — it's clean, typed, tested Python with proper packaging and tooling.


## Install & run
 
```bash
uv sync                        # install the package + deps into a venv
uv run logstats sample.log --top 5
```

After uv sync the logstats command exists inside the venv — the argument is a positional path to the log file, followed by options.

## Usage

Log lines are expected as TIMESTAMP LEVEL MESSAGE, e.g.

2026-07-13T09:15:42 INFO Starting logstats service v0.2.
 
### Top-N most frequent messages (--top):

```bash
$ uv run logstats sample.log --top 5
Top 5 All messages:
    5 x Error: Database connection failed: timeout after 30s
    1 x Info: Starting logstats service v0.2
    1 x Debug: Loading config from /etc/logstats/config.toml
    1 x Info: Listening on 0.0.0.0:8080
    1 x Warning: Disk usage at 82% on /var
```

### Filter by level (--level), combined with --top:

```bash
$ uv run logstats sample.log --level ERROR --top 3
Top 3 Error messages:
    5 x Error: Database connection failed: timeout after 30s
    1 x Error: Failed to write to disk: no space left on device
```
 
### Requests per hour (--per-hour):

```bash
$ uv run logstats sample.log --per-hour
All messages per hour:
    2026-07-13 09:00     9
    2026-07-13 10:00     6
    2026-07-13 11:00     1
    2026-07-13 13:00     1
    2026-07-14 18:00     1
```
  
With no view flag, logstats prints every (optionally level-filtered) entry.
Add `--verbose` to see diagnostic logs (malformed lines, empty results) on stderr.
`--top` and `--per-hour` are mutually exclusive. See logstats `--help` for the full list.

## Options

| Option | Description | 
| --- | --- | 
| `FILENAME` | Path to the log file (positional, required) |
|`--level {DEBUG,INFO,WARNING,ERROR}` | Only count entries at this level |
| `--top N` | Show the N most frequent messages |
| `--per-hour` | Bucket entries by hour |
| `--verbose`  | Emit diagnostic logs to stderr |
| `--help` | Show usage and exit  |


## Tech

Python 3.12+ · [`uv`](https://docs.astral.sh/uv/) · `click` · `pytest` · [`ruff`](https://docs.astral.sh/ruff/) · [`mypy`](https://mypy-lang.org/) · type hints & dataclasses throughout.

## License

MIT — see [LICENSE](LICENSE).
