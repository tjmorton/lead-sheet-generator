"""Entry point for test-harness — publishes an example message and exits."""

import logging

from .utils import configure_logging, publish_message

configure_logging()

logger = logging.getLogger(__name__)


def main() -> None:
    """Publish an example audio-analysis message to RabbitMQ, then exit."""
    logger.info("Starting test-harness")
    publish_message()
    logger.info("Test message published successfully — exiting")


if __name__ == "__main__":
    main()
