"""Tests for environment loading and validation."""

from __future__ import annotations

import importlib
import sys
from unittest.mock import patch

import pytest

MODULE = "audio_detection.utils.environment"
_REQUIRED_ENV = {
    "RABBITMQ_HOST": "localhost",
    "RABBITMQ_PORT": "5672",
    "RABBITMQ_QUEUE_NAME": "queue",
    "RABBITMQ_USER": "guest",
    "RABBITMQ_PASSWORD": "guest",
    "AWS_ENDPOINT_URL": "http://localhost:4566",
    "AWS_ACCESS_KEY_ID": "test",
    "AWS_SECRET_ACCESS_KEY": "test",
    "AWS_REGION": "us-east-1",
    "S3_BUCKET_NAME": "test-bucket",
    "WEB_APP_HOST": "http://localhost:3000",
}


@pytest.fixture(autouse=True)
def _reset_environment_module():
    yield
    sys.modules.pop(MODULE, None)


def _import_environment(monkeypatch, **overrides):
    for key in _REQUIRED_ENV:
        monkeypatch.delenv(key, raising=False)
    for key, value in {**_REQUIRED_ENV, **overrides}.items():
        if value is None:
            monkeypatch.delenv(key, raising=False)
        else:
            monkeypatch.setenv(key, value)
    sys.modules.pop(MODULE, None)
    return importlib.import_module(MODULE)


class TestGetRequiredEnv:
    def test_returns_value_when_set(self):
        from audio_detection.utils import environment as env

        with patch.object(env.os, "getenv", return_value="my-value"):
            assert env._get_required_env("SOME_VAR") == "my-value"

    def test_raises_when_missing(self):
        from audio_detection.utils import environment as env

        with (
            patch.object(env.os, "getenv", return_value=None),
            pytest.raises(ValueError, match=r"SOME_VAR.*required"),
        ):
            env._get_required_env("SOME_VAR")

    def test_raises_when_empty_string(self):
        from audio_detection.utils import environment as env

        with (
            patch.object(env.os, "getenv", return_value=""),
            pytest.raises(ValueError, match=r"SOME_VAR.*required"),
        ):
            env._get_required_env("SOME_VAR")


class TestGetEnvWithDefault:
    def test_returns_value_when_set(self):
        from audio_detection.utils import environment as env

        with patch.object(env.os, "getenv", return_value="custom"):
            assert env._get_env_with_default("VAR", "default") == "custom"

    def test_returns_default_when_missing(self):
        from audio_detection.utils import environment as env

        with patch.object(env.os, "getenv", return_value=None):
            assert env._get_env_with_default("VAR", "default") == "default"

    def test_returns_default_when_empty_string(self):
        from audio_detection.utils import environment as env

        with patch.object(env.os, "getenv", return_value=""):
            assert env._get_env_with_default("VAR", "default") == "default"


class TestGetEnvAsBoolean:
    def test_returns_true(self):
        from audio_detection.utils import environment as env

        with patch.object(env.os, "getenv", return_value="True"):
            assert env._get_env_as_boolean("FLAG", False) is True

    def test_returns_false(self):
        from audio_detection.utils import environment as env

        with patch.object(env.os, "getenv", return_value="False"):
            assert env._get_env_as_boolean("FLAG", True) is False

    def test_accepts_lowercase_true(self):
        from audio_detection.utils import environment as env

        with patch.object(env.os, "getenv", return_value="true"):
            assert env._get_env_as_boolean("FLAG", False) is True

    def test_accepts_lowercase_false(self):
        from audio_detection.utils import environment as env

        with patch.object(env.os, "getenv", return_value="false"):
            assert env._get_env_as_boolean("FLAG", True) is False

    def test_returns_default_when_missing(self):
        from audio_detection.utils import environment as env

        with patch.object(env.os, "getenv", return_value=None):
            assert env._get_env_as_boolean("FLAG", True) is True

    def test_returns_default_when_empty_string(self):
        from audio_detection.utils import environment as env

        with patch.object(env.os, "getenv", return_value=""):
            assert env._get_env_as_boolean("FLAG", True) is True

    def test_raises_on_invalid_value(self):
        from audio_detection.utils import environment as env

        with (
            patch.object(env.os, "getenv", return_value="not_bool"),
            pytest.raises(ValueError, match=r"FLAG.*True or False"),
        ):
            env._get_env_as_boolean("FLAG", False)


class TestGetEnvironment:
    def test_returns_cached_dict(self, monkeypatch):
        module = _import_environment(monkeypatch)
        result = module.get_environment()
        assert isinstance(result, dict)
        assert result["rabbitmq_host"] == "localhost"
        assert result["rabbitmq_port"] == 5672
        assert result["rabbitmq_queue_name"] == "queue"
        assert result["aws_region"] == "us-east-1"
        assert result["s3_bucket_name"] == "test-bucket"
        assert result["web_app_host"] == "http://localhost:3000"


def test_import_loads_required_env_vars(monkeypatch):
    module = _import_environment(monkeypatch)
    config = module.get_environment()
    assert config["rabbitmq_port"] == 5672
    assert config["rabbitmq_host"] == "localhost"


def test_import_fails_when_required_var_missing(monkeypatch):
    with pytest.raises(ValueError, match="WEB_APP_HOST"):
        _import_environment(monkeypatch, WEB_APP_HOST=None)