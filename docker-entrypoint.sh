#!/bin/sh
# Container entrypoint: runs logstats once and exits.
#   Input:  positional args if given, else $LOGSTATS_INPUT (required then).
#   Output: stdout goes to $LOGSTATS_OUTPUT when set, else stdout.
#   Extra args (e.g. --json) are passed to logstats unchanged.
set -eu

if [ "$#" -eq 0 ]; then
    set -- "${LOGSTATS_INPUT:?set LOGSTATS_INPUT or pass the input path as an argument}"
fi

if [ -n "${LOGSTATS_OUTPUT:-}" ]; then
    exec logstats "$@" > "$LOGSTATS_OUTPUT"
fi
exec logstats "$@"
