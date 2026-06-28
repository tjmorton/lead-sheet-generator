"""Utilites for RabbitMQ"""

import logging

import pika

from .environment import get_environment

config = get_environment()
logger = logging.getLogger(__name__)


def ensure_rabbitmq_queue() -> None:
    """Declare RabbitMQ queue if it doesn't exist.

    Raises
    ------
    Exception
        If queue declaration fails
    """
    logger.info("Bootstrapping RabbitMQ")

    # Get values from environment
    host = config["rabbitmq_host"]
    port = config["rabbitmq_port"]
    queue_name = config["rabbitmq_queue_name"]
    user = config["rabbitmq_user"]
    password = config["rabbitmq_password"]

    logger.debug("Using queue name %s", queue_name)

    credentials = pika.PlainCredentials(user, password)

    connection_params = pika.ConnectionParameters(host=host, port=port, credentials=credentials)

    try:
        # TODO: (tjm) Is there an asyncio equivalent of this?
        connection = pika.BlockingConnection(connection_params)
        channel = connection.channel()

        # Declaring a queue is idempotent, so we can run this on startup
        #   every time without problem
        channel.queue_declare(queue=queue_name, durable=True)

        # TODO: (tjm) Not the end of the world, but we could re-use this
        #   connection handle I think
        logger.debug("RabbitMQ queue ready, closing connection")
        connection.close()
    except Exception as e:
        logger.error("Failed to bootstrap RabbitMQ, %s", e)
        raise

    logger.info("Finished bootstrapping RabbitMQ")
