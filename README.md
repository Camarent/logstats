# logstats

[![CI](https://github.com/Camarent/logstats/actions/workflows/ci.yml/badge.svg)](https://github.com/Camarent/logstats/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/Camarent/logstats/branch/master/graph/badge.svg)](https://codecov.io/gh/Camarent/logstats)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Release](https://img.shields.io/github/v/release/Camarent/logstats)](https://github.com/Camarent/logstats/releases)

Statistics from log files — top-N messages, per-hour buckets, and level filtering —
available both as a CLI and as an HTTP API. Sources can be local paths or URLs, and
multiple sources are fetched concurrently.

> **Status:** alpha (`0.1.0`).
> The point isn't the tool's novelty — it's clean, typed, tested Python with proper packaging and tooling.

## Install

```bash
uv sync                        # install the package + deps into a venv
```

After `uv sync` the `logstats` command exists inside the venv.

## CLI

```bash
uv run logstats sample.log --top 5
```

Log lines are expected as `TIMESTAMP LEVEL MESSAGE`, e.g.

```
2026-07-13T09:15:42 INFO Starting logstats service v0.2
```

### Top-N most frequent messages (`--top`)

```bash
$ uv run logstats sample.log --top 5
[sample.log] Top 5 All messages:
    5 x Error: Database connection failed: timeout after 30s
    1 x Info: Starting logstats service v0.2
    1 x Debug: Loading config from /etc/logstats/config.toml
    1 x Info: Listening on 0.0.0.0:8080
    1 x Warning: Disk usage at 82% on /var
```

### Filter by level (`--level`)

```bash
$ uv run logstats sample.log --level ERROR --top 3
[sample.log] Top 3 Error messages:
    5 x Error: Database connection failed: timeout after 30s
    1 x Error: Failed to write to disk: no space left on device
```

### Entries per hour (`--per-hour`)

```bash
$ uv run logstats sample.log --per-hour
[sample.log] All messages per hour:
    2026-07-13 09:00     9
    2026-07-13 10:00     6
    2026-07-13 11:00     1
    2026-07-13 13:00     1
    2026-07-14 18:00     1
```

### Multiple sources

Any number of paths or URLs can be passed. By default each source gets its own report;
`-c` merges them into one.

```bash
uv run logstats sample.log https://example.com/app.log --top 3       # one report per source
uv run logstats sample.log https://example.com/app.log --top 3 -c    # single combined report
```

Each report header is labelled with the source it came from — `[sample.log]`, `[app.log]` —
so per-source reports stay distinguishable. A combined report is labelled `[All]`.

Sources are fetched concurrently. A source that fails (missing file, HTTP error) is
reported as a warning and the remaining sources still produce output.

With no view flag, `logstats` prints every (optionally level-filtered) entry.
`--top` and `--per-hour` are mutually exclusive.

### Options

| Option | Description |
| --- | --- |
| `SOURCES...` | One or more log file paths or `http(s)` URLs (positional, required) |
| `--level {DEBUG,INFO,WARNING,ERROR}` | Only count entries at this level |
| `--top N` | Show the N most frequent messages (N ≥ 1) |
| `--per-hour` | Bucket entries by hour |
| `-c` | Combine all sources into a single report |
| `--json` | Print reports as a JSON array of `{source, header, lines}` objects |
| `-v`, `--verbose` | Emit diagnostic logs to stderr |
| `--help` | Show usage and exit |

## Library API

The package re-exports four functions from `logstats`:

- `stream_lines(source: str, client: httpx.AsyncClient) -> AsyncIterator[str]`: yields raw lines from an HTTP(S) URL or a local path.
- `parse_line(line: str, level: LogType | None) -> LogEntry | None`: parses one line; returns `None` when the line is invalid or filtered out by `level`.
- `compute_top(entries: Iterable[LogEntry], source: str, *, level: LogType | None, top: int) -> TopStats`: returns the `top` most frequent messages and the total count.
- `compute_per_hour(entries: Iterable[LogEntry], source: str, *, level: LogType | None) -> HourlyStats`: returns entry counts bucketed by date and hour.

### Shard counters

`logstats.shard` counts entries per `(level, message)` key and merges the counts from several inputs:

- `shard_counts(entries: Iterable[LogEntry]) -> Counter[ShardKey]`: counts entries per key.
- `to_json(counter: Counter[ShardKey]) -> str`: serializes a counter to a JSON array of `[level, message, count]` rows.
- `from_json(text: str) -> Counter[ShardKey]`: reads a counter back from `to_json` output.
- `merge(counters: Iterable[Counter[ShardKey]]) -> Counter[ShardKey]`: sums several counters into one.

## HTTP API

### Configuring sources

The API never fetches arbitrary URLs. Sources are registered by name in `sources.toml`:

```toml
[sources]
app1 = "http://logs.internal/app1.log"
app2 = "local/path/app2.log"
```

Clients reference the **name**, never the location. Set `LOGSTATS_SOURCES` to point at a
different config file; it defaults to `sources.toml` in the working directory. The file is
loaded and validated once at startup, so a malformed config fails fast.

### Running

```bash
uv run uvicorn logstats.api:app --reload
```

Interactive docs render at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

### Endpoints

The `/stats/*` endpoints accept repeated `sources` params and an optional `level`.

| Endpoint | Returns |
| --- | --- |
| `GET /stats/top` | Top-N message counts (JSON) |
| `GET /stats/per-hour` | Per-hour entry counts (JSON) |
| `GET /stats/regular` | Raw entries as a Server-Sent Events stream |
| `GET /health` | `{"status": "ok"}` — liveness check, takes no params |

| Query param | Applies to | Description |
| --- | --- | --- |
| `sources` | all `/stats/*` | Registered source name; repeat for multiple |
| `level` | all `/stats/*` | `DEBUG`/`INFO`/`WARNING`/`ERROR` (case-insensitive) |
| `top` | `/stats/top` | Number of messages to return (≥ 1, default 3) |
| `combined` | `/stats/top`, `/stats/per-hour` | Merge all sources into one result (default `false`) |

```bash
$ curl "localhost:8000/stats/top?sources=app1&top=1"
{
  "results": [
    {
      "source": "app1",
      "level": "All",
      "top": 1,
      "total": 18,
      "messages": [
        {"level": "Error", "message": "Database connection failed: timeout after 30s", "count": 5}
      ]
    }
  ],
  "errors": []
}
```

Pass `sources` more than once to query several at a time, and add `combined=true` to merge
them into a single result labelled `All`.

Sources that fail to fetch do not fail the request — they are listed in `errors` while the
remaining sources still return results:

```json
{"results": [...], "errors": [{"source": "app2", "error": "[Errno 2] No such file or directory: 'app2.log'"}]}
```

An unknown source name or level returns `422`.

### Streaming

`GET /stats/regular` streams entries as they are read rather than buffering them, using
Server-Sent Events. Each event carries its type both in the SSE `event:` line and in the
payload:

```bash
$ curl -N "localhost:8000/stats/regular?sources=app1&level=ERROR"
event: entry
data: {"type":"entry","source":"app1","level":"Error","timestamp":"2026-07-13T09:15:42","message":"Boom"}

event: source_error
data: {"type":"source_error","source":"app2","error":"[Errno 2] No such file or directory"}
```

Because the response status is committed before streaming begins, a source that fails
mid-stream is reported as a `source_error` event rather than an HTTP error.

Aggregations (`/stats/top`, `/stats/per-hour`) cannot stream — they need every entry before
producing a result — so only the raw view is streamed.

## Container

The image runs `logstats` once and exits. Build it, then mount the log directory:

```bash
docker build -t logstats .
docker run --rm -v "$PWD:/data" logstats /data/sample.log --top 5
```

- Input: the arguments, passed to `logstats` unchanged. With no arguments, `LOGSTATS_INPUT` gives the input path (required then). When you pass options, put the input path in the arguments: `LOGSTATS_INPUT` is then ignored.
- Output: stdout, or the file at `LOGSTATS_OUTPUT` when set (the path must be writable inside the container).

```bash
docker run --rm -v "$PWD:/data" -e LOGSTATS_OUTPUT=/data/report.json logstats /data/sample.log --json
```

## Development

Run the full check suite (ruff, format check, mypy, pytest):

```bash
scripts/ci.sh
```

Run tests with a coverage report:

```bash
uv run pytest --cov=src/logstats --cov-report=term-missing
```

Enable the repo's git hooks (secret scan, commit-message check, pre-push checks):

```bash
git config core.hooksPath .githooks
```

CI runs the same checks on every push and pull request. See [CONTRIBUTING.md](CONTRIBUTING.md).

## Tech

Python 3.12+ · [`uv`](https://docs.astral.sh/uv/) · `click` · `FastAPI` · `pydantic` ·
`httpx` · `uvicorn` · `pytest` · `hypothesis` · [`ruff`](https://docs.astral.sh/ruff/) ·
[`mypy`](https://mypy-lang.org/) (strict) · type hints & dataclasses throughout.

## License

MIT — see [LICENSE](LICENSE).
