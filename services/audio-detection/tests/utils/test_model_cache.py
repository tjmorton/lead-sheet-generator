"""
Python patching primer for the Node developer:

In Node, jest.mock("module") intercepts the entire module at import time.
In Python, unittest.mock.patch("path.to.name") patches a name lookup —
  the dotted path is resolved at call time, and it matters *where* the
  production code imports from.

  If production code does:
      from demucs.pretrained import get_model          # module-level
    the name `get_model` is bound in model_cache's own namespace.  To
    mock it you must patch model_cache.get_model, NOT demucs.pretrained.get_model.

  If production code does:
      from demucs.pretrained import get_model          # inside a function body
    the import runs fresh every call, so patching the *source*
    demucs.pretrained.get_model works — each call re-imports the patched version.

Our production module uses module-level imports everywhere, so all patches
target model_cache's namespace via this prefix.
"""

import os
from unittest.mock import MagicMock, patch

import pytest

from audio_detection.utils import model_cache

# Dotted path prefix for patching names inside the module under test
_PATCH_PREFIX = "audio_detection.utils.model_cache"


class TestCheckDemucs:
    def test_cached_no_download(self):
        with (
            patch(f"{_PATCH_PREFIX}.get_model") as mock_get_model,
            patch.object(os, "listdir", return_value=["a.th", "b.th"]),
            patch.object(os.path, "isdir", return_value=True),
        ):
            model_cache._check_demucs()

        mock_get_model.assert_not_called()

    def test_empty_cache_downloads(self):
        listdir_responses = [[], ["a.th", "b.th"]]
        mock_listdir = MagicMock(side_effect=listdir_responses)

        with (
            patch(f"{_PATCH_PREFIX}.get_model") as mock_get_model,
            patch.object(os, "listdir", mock_listdir),
            patch.object(os.path, "isdir", return_value=True),
        ):
            model_cache._check_demucs()

        mock_get_model.assert_called_once_with("htdemucs")

    def test_cache_dir_missing_triggers_download(self):
        listdir_responses = [[], ["x.th"]]
        mock_listdir = MagicMock(side_effect=listdir_responses)

        with (
            patch(f"{_PATCH_PREFIX}.get_model") as mock_get_model,
            patch.object(os, "listdir", mock_listdir),
            patch.object(os.path, "isdir", return_value=False),
        ):
            model_cache._check_demucs()

        mock_get_model.assert_called_once()


class TestCheckBasicPitch:
    def test_files_present_passes(self):
        with (
            patch(f"{_PATCH_PREFIX}.basic_pitch.__file__", "/fake/basic_pitch/__init__.py"),
            patch.object(os, "walk", return_value=[("/p", [], ["a.onnx", "b.tflite"])]),
        ):
            model_cache._check_basic_pitch()

    def test_no_files_raises(self):
        with (
            patch(f"{_PATCH_PREFIX}.basic_pitch.__file__", "/fake/basic_pitch/__init__.py"),
            patch.object(os, "walk", return_value=[]),
            pytest.raises(FileNotFoundError, match="basic_pitch"),
        ):
            model_cache._check_basic_pitch()


class TestCheckCrema:
    def test_all_files_present_passes(self):
        with (
            patch(
                f"{_PATCH_PREFIX}.crema.models.__file__",
                "/fake/crema/models/__init__.py",
            ),
            patch("pathlib.Path.exists", return_value=True),
        ):
            model_cache._check_crema()

    def test_some_files_missing_raises(self):
        def _fake_exists(self):
            return self.name == "model.h5"

        with (
            patch(
                f"{_PATCH_PREFIX}.crema.models.__file__",
                "/fake/crema/models/__init__.py",
            ),
            patch("pathlib.Path.exists", _fake_exists),
            pytest.raises(FileNotFoundError, match="crema"),
        ):
            model_cache._check_crema()


class TestCheckMadmom:
    def test_pkl_files_present_passes(self):
        fake_walk = [("/fake/madmom/models", [], ["a.pkl", "b.pkl"])]
        with (
            patch.object(os, "walk", return_value=fake_walk),
            patch(f"{_PATCH_PREFIX}.madmom.models.__file__", "/fake/madmom/models/__init__.py"),
        ):
            model_cache._check_madmom()

    def test_no_pkl_files_raises(self):
        with (
            patch.object(os, "walk", return_value=[]),
            patch(f"{_PATCH_PREFIX}.madmom.models.__file__", "/fake/madmom/models/__init__.py"),
            pytest.raises(FileNotFoundError, match="madmom"),
        ):
            model_cache._check_madmom()


class TestEnsureMLModels:
    def test_all_checks_pass(self):
        with (
            patch.object(model_cache, "_check_demucs"),
            patch.object(model_cache, "_check_basic_pitch"),
            patch.object(model_cache, "_check_crema"),
            patch.object(model_cache, "_check_madmom"),
        ):
            model_cache.ensure_ml_models()

    def test_one_check_fails_raises(self):
        with (
            patch.object(model_cache, "_check_demucs"),
            patch.object(model_cache, "_check_basic_pitch"),
            patch.object(
                model_cache,
                "_check_crema",
                side_effect=FileNotFoundError("no crema"),
            ),
            patch.object(model_cache, "_check_madmom"),
            pytest.raises(Exception, match="Failed to ensure ML models"),
        ):
            model_cache.ensure_ml_models()
