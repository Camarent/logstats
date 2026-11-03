# Changelog

All notable changes to this project are documented here.

## [0.1.0]

- First release: CLI (`--top`, `--level`, `--per-hour`, `-c`, `-v`) and HTTP API
  (`/stats/top`, `/stats/per-hour`, `/stats/regular` SSE, `/health`) over log files and URLs.
- Sources fetched concurrently; failing sources reported as warnings or `errors` entries.
- API sources registered by name in `sources.toml` (`LOGSTATS_SOURCES` overrides the path).
