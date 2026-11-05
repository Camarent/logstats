# Changelog

All notable changes to this project are documented here.

## [Unreleased]

- Library API: `stream_lines`, `parse_line`, `compute_top` and `compute_per_hour` re-exported from `logstats` (#26).
- Shard counters: `logstats.shard` gains `shard_counts`, `to_json`, `from_json` and `merge` for serializable, mergeable counts (#27).
- CLI: `--json` prints reports as a JSON array (#28).
- Container: entrypoint runs `logstats` once; input by argument or `LOGSTATS_INPUT`, output to stdout or `LOGSTATS_OUTPUT` (#29).

## [0.1.0]

- First release: CLI (`--top`, `--level`, `--per-hour`, `-c`, `-v`) and HTTP API
  (`/stats/top`, `/stats/per-hour`, `/stats/regular` SSE, `/health`) over log files and URLs.
- Sources fetched concurrently; failing sources reported as warnings or `errors` entries.
- API sources registered by name in `sources.toml` (`LOGSTATS_SOURCES` overrides the path).
