FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:0.11.23 /uv /usr/local/bin/uv

WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PATH="/app/.venv/bin:$PATH"

COPY pyproject.toml uv.lock README.md ./
COPY src ./src
RUN uv sync --frozen --no-dev

COPY docker-entrypoint.sh ./
RUN chmod +x docker-entrypoint.sh

COPY sources.toml ./
ENV LOGSTATS_SOURCES=/app/sources.toml

RUN useradd -r -u 10001 app
USER app

ENTRYPOINT ["/app/docker-entrypoint.sh"]
