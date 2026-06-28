"""Ensure ML models we use throughout the app are available

Most of these download on first use - which is not ideal
"""

import logging
import os
from pathlib import Path  # Used to get model path for basic_pitch and madmom

import basic_pitch
import crema.models
import madmom.models
from demucs.pretrained import get_model  # Used to download model for demucs

logger = logging.getLogger(__name__)


def _check_demucs() -> None:
    """Check if we already have the model in it's expected location

    If we don't, download it via demucs get_model()

    If expected path changes, this is expected to break
    """
    logger.info("Checking demucs")

    # TODO: (tjm) This cache path is not going to work on Windows
    #   I should make the expectation clear that this should be run in a container
    cache = os.path.expanduser("~/.cache/torch/hub/checkpoints")

    existing = os.listdir(cache) if os.path.isdir(cache) else []
    th_files = [f for f in existing if f.endswith(".th")]
    if th_files:
        logger.debug("cached (%s .th files)", len(th_files))
    else:
        logger.debug("downloading htdemucs")
        get_model("htdemucs")
        new = [f for f in os.listdir(cache) if f.endswith(".th")]
        logger.debug("downloaded (%s .th files)", len(new))

    logger.info("Finished checking demucs")


def _check_basic_pitch() -> None:
    """Verify basic_pitch bundled model files exist"""

    logger.info("Checking basic_pitch")

    model_dir = str(Path(basic_pitch.__file__).parent / "saved_models" / "icassp_2022")
    logger.debug("host: pretrained_models/basic_pitch/")
    logger.debug("container: %s", model_dir)

    n_files = sum(1 for _r, _d, fs in os.walk(model_dir) for _ in fs)
    if n_files == 0:
        raise FileNotFoundError(f"basic_pitch model files not found at {model_dir}")
    logger.info("%s model files found", n_files)


def _check_crema() -> None:
    """Verify crema bundled model files exist"""

    logger.info("Checking crema")

    model_dir = str(Path(crema.models.__file__).parent / "chord")
    logger.debug("host: pretrained_models/crema/")
    logger.debug("container: %s", model_dir)

    expected = ["model.h5", "model_spec.pkl", "pump.pkl", "version.txt"]
    found = [f for f in expected if (Path(model_dir) / f).exists()]
    if len(found) < len(expected):
        missing = [f for f in expected if f not in found]
        raise FileNotFoundError(f"crema model files missing at {model_dir}: {missing}")
    logger.info("%s/%s expected files found", len(found), len(expected))


def _check_madmom() -> None:
    """Verify madmom bundled model files exist"""

    logger.info("Checking madmom")

    models_dir = str(Path(madmom.models.__file__).parent)
    logger.debug("host: pretrained_models/madmom/")
    logger.debug("container: %s", models_dir)

    pkl_count = 0
    for _root, _dirs, files in os.walk(models_dir):
        pkl_count += sum(1 for f in files if f.endswith(".pkl"))
    if pkl_count == 0:
        raise FileNotFoundError(f"madmom model files not found at {models_dir}")
    logger.info("%s .pkl files found", pkl_count)


def ensure_ml_models() -> None:
    """Ensures the ML models we use today are available"""
    logger.info("Ensure ML models are available")

    checks = [
        ("demucs (stem separation) - downloads at runtime", _check_demucs),
        ("basic-pitch (MIDI transcription) - bundled in wheel", _check_basic_pitch),
        ("crema (chord detection) - bundled in wheel", _check_crema),
        ("madmom (beat detection / key detection) - bundled in wheel", _check_madmom),
    ]

    for check_label, check_fn in checks:
        logger.debug("Checking %s", check_label)
        try:
            check_fn()
        except Exception as e:
            logger.error("Failed to check %s, with error: %s", check_label, e)
            raise Exception("Failed to ensure ML models") from e

    logger.info("All ML models available")
