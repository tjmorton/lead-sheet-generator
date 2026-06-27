FROM python:3.11-slim AS base

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

# Install system dependencies for audio processing
# - sox and codecs for audio file loading (mp3, ogg, flac, etc.)
# - build tools for compiling madmom from source
# - git for installing madmom from GitHub
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    sox \
    libsox-dev \
    libsox-fmt-all \
    libmp3lame0 \
    libvorbis0a libvorbisenc2 libvorbisfile3 \
    libflac-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install dependencies first (cached unless pyproject.toml/uv.lock change).
# The --mount=type=cache persists uv's download cache across rebuilds so
# packages are not re-downloaded even when the layer is invalidated.
COPY pyproject.toml uv.lock README.md ./
COPY src/ ./src/
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# Pre-download the Demucs htdemucs model weights (~80 MB) so they are
# baked into the image layer and not re-downloaded on every container start.
# The same weights work for both CPU and CUDA inference.
RUN uv run --no-sync python -c \
    "from demucs.pretrained import get_model; get_model('htdemucs')"

# Development target - uses volume mounts for hot reload
FROM base AS dev
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen
CMD ["uv", "run", "--no-sync", "song-chords"]

# Production target - runs the application
FROM base AS production
CMD ["uv", "run", "--no-sync", "song-chords"]

# Test target - runs tests
FROM base AS test
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen
COPY tests/ ./tests/
CMD ["uv", "run", "--no-sync", "pytest", "-v"]

