"""Entry point for audio-detection queue processing"""

import logging

from .utils import (
    configure_logging,
    ensure_rabbitmq_queue,
    ensure_s3_bucket,
    start_listener,
)

configure_logging()

logger = logging.getLogger(__name__)


def main():
    """Long running process that consumes a rabbitMQ queue

    Processes audio referenced by s3 URL in queue message

    POSTs results to web-app service
    """
    logger.info("Starting audio-detection service")

    # We have to lazy import this. One of the imports under ensure_ml_models
    # adds a StreamHandler <stderr> to Python's root logger during its own import.
    # After that, logging.basicConfig() fails because the root logger already has
    # handlers.
    # TODO: (tjm) Understand this more - I must be missing something

    # NOTE: onnxruntime emits a device_discovery C++ warning at import time.
    # pybind hardcodes the severity, so no env var suppresses it.
    # If you want to suppress it, grab suppress_stderr() from .utils.logging:
    #
    #     from .utils.logging import suppress_stderr
    #     with suppress_stderr():
    #         from .utils.model_cache import ensure_ml_models
    #
    # https://github.com/microsoft/onnxruntime/pull/27645
    from .utils.model_cache import ensure_ml_models

    logger.info("Ensuring ML models are present")
    ensure_ml_models()

    logger.info("Ensuring RabbitMQ queue exists")
    ensure_rabbitmq_queue()

    logger.info("Ensuring S3 bucket exists")
    ensure_s3_bucket()

    logger.info("Starting RabbitMQ queue listener")
    start_listener()


if __name__ == "__main__":
    main()
