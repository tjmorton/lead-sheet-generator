"""Message handlers for RabbitMQ messages"""

import logging

from ..utils.environment import get_environment

config = get_environment()
logger = logging.getLogger(__name__)

def process_message(message_body: dict) -> None:
    """Process RabbitMQ message"""
    logger.info("Processing RabbitMQ message")
    logger.debug("Message body is %s", message_body)