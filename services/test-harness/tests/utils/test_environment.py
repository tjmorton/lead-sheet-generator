import importlib
import sys

import pytest

MODULE = "test_harness.utils.environment"
_REQUIRED_ENV = [
    "RABBITMQ_HOST",
    "RABBITMQ_PORT",
    "RABBITMQ_QUEUE_NAME",
    "RABBITMQ_USER",
    "RABBITMQ_PASSWORD",
]


@pytest.fixture(autouse=True)
def _reset_module() -> None:
    yield
    sys.modules.pop(MODULE, None)


def _import_module(monkeypatch, **overrides: str) -> object:
    for key in _REQUIRED_ENV:
        monkeypatch.delenv(key, raising=False)
    defaults = {
        "RABBITMQ_HOST": "localhost",
        "RABBITMQ_PORT": "5672",
        "RABBITMQ_QUEUE_NAME": "test-queue",
        "RABBITMQ_USER": "guest",
        "RABBITMQ_PASSWORD": "guest",
    }
    env = {**defaults, **overrides}
    for key, value in env.items():
        if value is None:
            monkeypatch.delenv(key, raising=False)
        else:
            monkeypatch.setenv(key, str(value))
    sys.modules.pop(MODULE, None)
    return importlib.import_module(MODULE)


class TestGetEnvironment:
    def test_returns_rabbitmq_config(self, monkeypatch) -> None:
        env = _import_module(monkeypatch)
        config = env.get_environment()

        assert config["rabbitmq_host"] == "localhost"
        assert config["rabbitmq_port"] == 5672
        assert config["rabbitmq_queue_name"] == "test-queue"
        assert config["rabbitmq_user"] == "guest"
        assert config["rabbitmq_password"] == "guest"

    def test_missing_host_raises_valueerror(self, monkeypatch) -> None:
        with pytest.raises(ValueError, match="RABBITMQ_HOST"):
            _import_module(monkeypatch, RABBITMQ_HOST=None)

    def test_missing_port_raises_valueerror(self, monkeypatch) -> None:
        with pytest.raises(ValueError, match="RABBITMQ_PORT"):
            _import_module(monkeypatch, RABBITMQ_PORT=None)
