"""App logging config."""

import logging
import sys


def configure_logging() -> None:
    """Configure the root-level app logging."""
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    logging.getLogger("pika").setLevel(logging.ERROR)
