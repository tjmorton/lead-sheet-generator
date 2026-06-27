import os
import sys
from unittest.mock import MagicMock, patch

from audio_detection import download_models


class TestCheckDemucs:
    def test_cached_reports_no_download(self, capsys):
        with patch("demucs.pretrained.get_model") as mock_get_model:
            with patch.object(os, "listdir", return_value=["a.th", "b.th"]):
                with patch.object(os.path, "isdir", return_value=True):
                    download_models._check_demucs()

        captured = capsys.readouterr().out
        assert "cached" in captured
        assert "a.th" in captured
        assert "b.th" in captured
        mock_get_model.assert_not_called()

    def test_empty_cache_downloads(self, capsys):
        listdir_responses = [[], ["a.th", "b.th"]]
        mock_listdir = MagicMock(side_effect=listdir_responses)

        with patch("demucs.pretrained.get_model") as mock_get_model:
            with patch.object(os, "listdir", mock_listdir):
                with patch.object(os.path, "isdir", return_value=True):
                    download_models._check_demucs()

        captured = capsys.readouterr().out
        assert "downloading" in captured
        assert "downloaded" in captured
        mock_get_model.assert_called_once()

    def test_cache_dir_missing_creates_and_downloads(self, capsys):
        listdir_responses = [[], ["x.th"]]
        mock_listdir = MagicMock(side_effect=listdir_responses)

        with patch("demucs.pretrained.get_model") as mock_get_model:
            with patch.object(os, "listdir", mock_listdir):
                with patch.object(os.path, "isdir", return_value=False):
                    download_models._check_demucs()

        captured = capsys.readouterr().out
        assert "downloading" in captured
        mock_get_model.assert_called_once()


class TestCheckBasicPitch:
    def test_model_path_is_resolved(self, capsys):
        with patch("basic_pitch.__file__", "/fake/site-packages/basic_pitch/__init__.py"):
            with patch.object(os, "walk", return_value=[("/fake/path", [], ["a.onnx", "b.tflite"])]):
                with patch.object(os.path, "exists", return_value=True):
                    download_models._check_basic_pitch()

        captured = capsys.readouterr().out
        assert "host: pretrained_models/basic_pitch/" in captured
        assert "2 files" in captured

    def test_zero_files_when_path_missing(self, capsys):
        with patch("basic_pitch.__file__", "/fake/site-packages/basic_pitch/__init__.py"):
            with patch.object(os, "walk", return_value=[]):
                with patch.object(os.path, "exists", return_value=False):
                    download_models._check_basic_pitch()

        captured = capsys.readouterr().out
        assert "0 files" in captured


class TestCheckCrema:
    def test_expected_files_present(self, capsys):
        with patch(
            "pkg_resources.resource_filename",
            return_value="/fake/crema/models/chord/model.h5",
        ):
            with patch("pathlib.Path.exists", return_value=True):
                download_models._check_crema()

        captured = capsys.readouterr().out
        assert "host: pretrained_models/crema/" in captured
        assert "4/4 expected files" in captured

    def test_some_files_missing(self, capsys):
        def _fake_exists(self):
            return self.name == "model.h5"

        with patch(
            "pkg_resources.resource_filename",
            return_value="/fake/crema/models/chord/model.h5",
        ):
            with patch("pathlib.Path.exists", _fake_exists):
                download_models._check_crema()

        captured = capsys.readouterr().out
        assert "1/4 expected files" in captured


class TestCheckMadmom:
    def test_reports_pkl_count(self, capsys):
        fake_walk = [("/fake/madmom/models", [], ["a.pkl", "b.pkl", "c.pkl"])]
        with patch.object(download_models.os, "walk", return_value=fake_walk):
            with patch(
                "madmom.models.__file__",
                "/fake/madmom/models/__init__.py",
            ):
                download_models._check_madmom()

        captured = capsys.readouterr().out
        assert "host: pretrained_models/madmom/" in captured
        assert "3 .pkl files" in captured


class TestMain:
    def test_all_checks_pass(self, capsys):
        with patch.object(download_models, "_check_demucs"):
            with patch.object(download_models, "_check_basic_pitch"):
                with patch.object(download_models, "_check_crema"):
                    with patch.object(download_models, "_check_madmom"):
                        download_models.main()

        captured = capsys.readouterr().out
        assert "All models ready." in captured

    def test_one_check_fails_exits_nonzero(self, capsys):
        with patch.object(download_models, "_check_demucs"):
            with patch.object(download_models, "_check_basic_pitch"):
                with patch.object(
                    download_models,
                    "_check_crema",
                    side_effect=ImportError("no crema"),
                ):
                    with patch.object(download_models, "_check_madmom"):
                        with patch.object(sys, "exit") as mock_exit:
                            download_models.main()

        mock_exit.assert_called_once_with(1)
