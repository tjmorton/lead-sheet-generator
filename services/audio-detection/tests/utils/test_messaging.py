"""Tests for RabbitMQ messaging utilities."""

from unittest.mock import MagicMock, patch

import pytest

from audio_detection.utils import messaging


class TestEnsureRabbitmqQueue:
    def test_declares_queue_and_closes(self):
        mock_connection = MagicMock()
        mock_channel = MagicMock()
        mock_connection.channel.return_value = mock_channel

        with patch("pika.BlockingConnection", return_value=mock_connection) as mock_conn:
            messaging.ensure_rabbitmq_queue()

        expected_queue = messaging.config["rabbitmq_queue_name"]
        mock_conn.assert_called_once()
        mock_channel.queue_declare.assert_called_once_with(
            queue=expected_queue, durable=True
        )
        mock_connection.close.assert_called_once()

    def test_raises_on_connection_failure(self):
        with (
            patch("pika.BlockingConnection", side_effect=Exception("connection refused")),
            pytest.raises(Exception, match="connection refused"),
        ):
            messaging.ensure_rabbitmq_queue()