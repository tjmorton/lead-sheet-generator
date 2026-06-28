FROM python:3.11-slim AS base

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

WORKDIR /app

COPY pyproject.toml uv.lock ./
COPY src/ ./src/
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

FROM base AS dev
CMD ["uv", "run", "--no-sync", "test-harness"]

FROM base AS test
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen
COPY tests/ ./tests/
CMD ["uv", "run", "--no-sync", "pytest", "-v"]
