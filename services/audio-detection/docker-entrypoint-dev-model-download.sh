#!/bin/bash
# ---------------------------------------------------------------------------
# Docker entrypoint for the DEV target only.
#
# Problem:
#   basic-pitch, crema, and madmom bundle their ML model weights inside the
#   pip package.  They land in site-packages during `uv sync`.  In dev we
#   volume-mount those site-packages paths to ./pretrained_models/ so that
#   model files survive container rebuilds.
#
#   On the *first* run the host directory is empty.  Docker mounts it over
#   the container path, hiding the models that `uv sync` just installed.
#   Without intervention the code would fail to find its models.
#
# Solution:
#   The Dockerfile caches a copy of each model directory to `/model_stash/`
#   at build time.  This script checks each volume mount on container start.
#   If the mount is empty, it copies from the stash into the volume.
#   On subsequent runs (or rebuilds where pretrained_models/ already has
#   files from a previous run) this is a no-op.
#
#   Demucs is different – it downloads at runtime to ~/.cache/torch/hub/.
#   That path is also volume-mounted, so the download naturally persists.
# ---------------------------------------------------------------------------
set -e

SITE_PACKAGES=$(uv run python -c "import sysconfig; print(sysconfig.get_paths()['purelib'])")

seed_if_empty() {
    local name="$1" dst="$2"
    if [ -d "$dst" ] && [ -z "$(ls -A "$dst" 2>/dev/null)" ]; then
        echo "entrypoint: populating ${name} from image stash..."
        cp -r /model_stash/"$name"/* "$dst"/
    fi
}

seed_if_empty basic_pitch "$SITE_PACKAGES/basic_pitch/saved_models/icassp_2022"
seed_if_empty crema       "$SITE_PACKAGES/crema/models/chord"
seed_if_empty madmom      "$SITE_PACKAGES/madmom/models"

exec "$@"
