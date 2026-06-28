import json
from unittest.mock import MagicMock, patch

import pytest

from test_harness.utils.messaging import publish_message


class TestPublishMessage:
    def test_publishes_expected_message_shape(self) -> None:
        mock_connection = MagicMock()
        mock_channel = MagicMock()
        mock_connection.channel.return_value = mock_channel

        with patch("pika.BlockingConnection", return_value=mock_connection) as mock_connection_cls:
            publish_message()

        mock_connection_cls.assert_called_once()
        mock_channel.queue_declare.assert_called_once_with(
            queue="audio-analysis-queue", durable=True
        )

        call_args = mock_channel.basic_publish.call_args
        assert call_args is not None
        kwargs = call_args[1]
        assert kwargs["exchange"] == ""
        assert kwargs["routing_key"] == "audio-analysis-queue"

        body = json.loads(kwargs["body"])
        assert body["s3_url"] == "s3://audio-analysis-files/test/example-song.mp3"
        assert body["playback"] == {"audioUrl": "s3://audio-analysis-files/test/example-song.mp3"}
        assert body["metadata"] == {
            "title": "Example Song",
            "artist": "Example Artist",
            "album": "Example Album",
            "year": 2024,
        }

        assert kwargs["properties"].delivery_mode == 2
        mock_connection.close.assert_called_once()

    def test_raises_on_connection_failure(self) -> None:
        with (
            patch("pika.BlockingConnection", side_effect=Exception("connection refused")),
            pytest.raises(Exception, match="connection refused"),
        ):
            publish_message()
