"""Utilites for RabbitMQ"""

import json
import logging

import pika

from ..handlers import process_message
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

    connection_params = pika.ConnectionParameters(
        host=host, port=port, credentials=credentials
    )

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


def _preprocess_message(ch, method, properties, body) -> None:
    """Preprocess message to pass to message handler"""
    logger.debug("Preprocessing RabbitMQ message")
    try:
        message_body = json.loads(body.decode("utf-8"))
        logger.debug("Received message %s", body)

        # Call the message hander with the json
        process_message(message_body)

        ch.basic_ack(delivery_tag=method.delivery_tag)
        logger.debug("Message processed and acknowledged")
    except Exception as e:
        logger.error("Failed to process message: %s", e)
        try:
            logger.debug("Acknowledging the failed message")
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as ack_err:
            logger.error("Failed to ack message after error: %s", ack_err)


def start_listener() -> None:
    """Start listening to RabbitMQ queue for audio analysis messages."""
    queue_name = config["rabbitmq_queue_name"]

    logger.info("Starting RabbitMQ listener for queue: %s", queue_name)
    logger.debug(
        "RabbitMQ host: %s:%s",
        config["rabbitmq_host"],
        config["rabbitmq_port"],
    )

    credentials = pika.PlainCredentials(
        config["rabbitmq_user"], config["rabbitmq_password"]
    )
    connection_params = pika.ConnectionParameters(
        host=config["rabbitmq_host"],
        port=config["rabbitmq_port"],
        credentials=credentials,
        heartbeat=0,
    )

    logger.debug("Connecting to RabbitMQ")
    try:
        connection = pika.BlockingConnection(connection_params)
        channel = connection.channel()
        channel.queue_declare(queue=queue_name, durable=True)
        channel.basic_qos(prefetch_count=1)

        channel.basic_consume(
            queue=queue_name,
            on_message_callback=_preprocess_message,
            auto_ack=False
        )
        
        logger.debug("Consuming RabbitMQ queue")
        try:
            channel.start_consuming()
        # CTRL + C to exit, TODO: (tjm) Need to change this to a real sigterm / sigint handler
        except KeyboardInterrupt:
            logger.info("Stopping listening")
            channel.stop_consuming()
        finally:
            connection.close()
            logger.info("Connection to RabbitMQ closed")
    except Exception as e:
        logger.error("Failed to connect to RabbitMQ")
        raise Exception("Failed to connect to RabbitMQ") from e
