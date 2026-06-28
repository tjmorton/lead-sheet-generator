"""Tests for logging configuration."""

import logging
import os
import warnings
from unittest.mock import patch

from audio_detection.utils import logging as logging_utils


class TestConfigureLogging:
    def test_sets_tf_level_when_not_already_set(self):
        key = "TF_CPP_MIN_LOG_LEVEL"
        original = os.environ.pop(key, None)
        try:
            logging_utils.configure_logging()
            assert os.environ[key] == "3"
        finally:
            if original is not None:
                os.environ[key] = original

    def test_does_not_override_existing_tf_level(self):
        key = "TF_CPP_MIN_LOG_LEVEL"
        original = os.environ.get(key)
        os.environ[key] = "2"
        try:
            logging_utils.configure_logging()
            assert os.environ[key] == "2"
        finally:
            if original is not None:
                os.environ[key] = original
            else:
                del os.environ[key]

    def test_suppresses_crema_future_warning(self):
        with patch.object(warnings, "filterwarnings") as mock_filter:
            logging_utils.configure_logging()

        mock_filter.assert_any_call("ignore", category=FutureWarning, module="crema")

    def test_suppresses_pkg_resources_warning(self):
        with patch.object(warnings, "filterwarnings") as mock_filter:
            logging_utils.configure_logging()

        mock_filter.assert_any_call("ignore", message="pkg_resources is deprecated")

    def test_silences_noisy_libraries(self):
        logging_utils.configure_logging()
        for lib in (
            "tensorflow",
            "absl",
            "h5py",
            "onnxruntime",
            "basic_pitch",
            "urllib",
            "botocore",
            "boto3",
            "pika",
        ):
            assert logging.getLogger(lib).level == logging.ERROR

    def test_configures_root_logger_at_debug(self):
        with patch("logging.basicConfig") as mock_basic_config:
            logging_utils.configure_logging()

        mock_basic_config.assert_called_once()
        _call_args, call_kwargs = mock_basic_config.call_args
        assert call_kwargs["level"] == logging.DEBUG
        assert len(call_kwargs["handlers"]) == 1
        assert isinstance(call_kwargs["handlers"][0], logging.StreamHandler)
