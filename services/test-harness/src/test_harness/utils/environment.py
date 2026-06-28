"""App config via environment variables.

Loads and validates environment variables at import time, ensuring all
required configuration is present before the application runs.
"""

import os


def _get_required_env(var_name: str) -> str:
    """Get a required environment variable. Raises a ValueError if missing."""
    value = os.getenv(var_name)
    if not value:
        raise ValueError(f"{var_name} environment variable is required but not set")
    return value


def _load_environment() -> dict:
    """Load and validate environment configuration."""
    config: dict = {
        "rabbitmq_host": _get_required_env("RABBITMQ_HOST"),
        "rabbitmq_port": int(_get_required_env("RABBITMQ_PORT")),
        "rabbitmq_queue_name": _get_required_env("RABBITMQ_QUEUE_NAME"),
        "rabbitmq_user": _get_required_env("RABBITMQ_USER"),
        "rabbitmq_password": _get_required_env("RABBITMQ_PASSWORD"),
    }

    return config


_ENVIRONMENT = _load_environment()


def get_environment() -> dict:
    """Get the validated environment config.

    Returns:
        dict: Dictionary containing environment configuration
    """
    return _ENVIRONMENT
