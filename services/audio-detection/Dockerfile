FROM python:3.11-slim AS base

# ---------------------------------------------------------------------------
# Model-weight strategy:
#
#   basic-pitch, crema, madmom  – weights are *bundled* in the pip package.
#                                 `uv sync` extracts them into site-packages.
#                                 Nothing downloads at runtime.
#
#   demucs                      – downloads htdemucs (~80 MB) at runtime
#                                 via torch.hub to ~/.cache/torch/hub/.
#
#   Dev target (docker compose):
#     Volume-mounts site-packages subdirs + torch hub cache to
#     ./pretrained_models/ on the host.  Models survive container
#     rebuilds.  The entrypoint seeds empty volumes from a build-time
#     stash on first run.
#
#   Production target (standalone):
#     No volume mounts.  All weights are baked into the image.
#     demucs is pre-downloaded with a RUN step so it never hits the
#     network at container start.
# ---------------------------------------------------------------------------

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

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

COPY pyproject.toml uv.lock README.md ./
COPY src/ ./src/
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# Build-time stash of bundled model files for the dev entrypoint.
# Volumes overlay site-packages at runtime, hiding the originals, so we
# need a separate copy in the image that the entrypoint can copy from.
RUN <<PYEOF uv run python -
import shutil
from pathlib import Path
import basic_pitch, crema.models, madmom.models
stash = Path('/model_stash')
stash.mkdir(exist_ok=True)
bp = Path(basic_pitch.__file__).parent / 'saved_models' / 'icassp_2022'
shutil.copytree(bp, stash / 'basic_pitch', dirs_exist_ok=True)
cm = Path(crema.models.__file__).parent / 'chord'
shutil.copytree(cm, stash / 'crema', dirs_exist_ok=True)
mm = Path(madmom.models.__file__).parent
shutil.copytree(mm, stash / 'madmom', dirs_exist_ok=True)
PYEOF

COPY docker-entrypoint-dev-model-download.sh /docker-entrypoint-dev-model-download.sh

# --- dev: volume-mounts pretrained_models/ for fast rebuilds ---
FROM base AS dev
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen
ENTRYPOINT ["/docker-entrypoint-dev-model-download.sh"]
CMD ["uv", "run", "--no-sync", "audio-detection"]

# --- production: no volumes, no entrypoint, models baked into image ---
FROM base AS production
RUN uv run python -c \
    "from demucs.pretrained import get_model; get_model('htdemucs')"
CMD ["uv", "run", "--no-sync", "song-chords"]

# --- test ---
FROM base AS test
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen
COPY tests/ ./tests/
CMD ["uv", "run", "--no-sync", "pytest", "-v"]
