"""Utilities for RabbitMQ publishing."""

import json
import logging

import pika

from .environment import get_environment

config = get_environment()
logger = logging.getLogger(__name__)


def publish_message() -> None:
    """Publish an example audio-analysis message to RabbitMQ.

    Connects to RabbitMQ, declares the queue, publishes a hardcoded
    example message in the shape expected by audio-detection, and
    disconnects.

    Raises
    ------
    Exception
        If connection or publishing fails
    """
    host = config["rabbitmq_host"]
    port = config["rabbitmq_port"]
    queue_name = config["rabbitmq_queue_name"]
    user = config["rabbitmq_user"]
    password = config["rabbitmq_password"]

    message: dict = {
        "s3_url": "s3://audio-analysis-files/test/example-song.mp3",
        "playback": {"audioUrl": "s3://audio-analysis-files/test/example-song.mp3"},
        "metadata": {
            "title": "Example Song",
            "artist": "Example Artist",
            "album": "Example Album",
            "year": 2024,
        },
    }

    logger.info("Publishing example message to queue: %s", queue_name)

    credentials = pika.PlainCredentials(user, password)
    connection_params = pika.ConnectionParameters(
        host=host,
        port=port,
        credentials=credentials,
    )

    try:
        connection = pika.BlockingConnection(connection_params)
        channel = connection.channel()

        channel.queue_declare(queue=queue_name, durable=True)

        channel.basic_publish(
            exchange="",
            routing_key=queue_name,
            body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=2),
        )

        logger.info("Message published: %s", json.dumps(message, indent=2))
        connection.close()
    except Exception as e:
        logger.error("Failed to publish message: %s", e)
        raise
