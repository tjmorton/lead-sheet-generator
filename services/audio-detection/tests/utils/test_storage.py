"""Tests for S3 storage utilities."""

from unittest.mock import MagicMock, patch

import pytest
from botocore.exceptions import ClientError

from audio_detection.utils import storage


class TestEnsureS3Bucket:
    def test_skips_creation_when_bucket_exists(self):
        mock_client = MagicMock()

        with patch("boto3.client", return_value=mock_client):
            storage.ensure_s3_bucket()

        expected_bucket = storage.config["s3_bucket_name"]
        mock_client.head_bucket.assert_called_once_with(Bucket=expected_bucket)
        mock_client.create_bucket.assert_not_called()

    def test_creates_bucket_when_not_found(self):
        mock_client = MagicMock()
        mock_client.head_bucket.side_effect = ClientError(
            {"Error": {"Code": "404"}}, "HeadBucket"
        )

        with patch("boto3.client", return_value=mock_client):
            storage.ensure_s3_bucket()

        expected_bucket = storage.config["s3_bucket_name"]
        mock_client.create_bucket.assert_called_once_with(expected_bucket)

    def test_raises_on_unexpected_head_error(self):
        mock_client = MagicMock()
        mock_client.head_bucket.side_effect = ClientError(
            {"Error": {"Code": "403"}}, "HeadBucket"
        )

        with (
            patch("boto3.client", return_value=mock_client),
            pytest.raises(ClientError),
        ):
            storage.ensure_s3_bucket()

        mock_client.create_bucket.assert_not_called()

    def test_raises_on_create_failure(self):
        mock_client = MagicMock()
        mock_client.head_bucket.side_effect = ClientError(
            {"Error": {"Code": "404"}}, "HeadBucket"
        )
        mock_client.create_bucket.side_effect = ClientError(
            {"Error": {"Code": "BucketAlreadyExists"}}, "CreateBucket"
        )

        with (
            patch("boto3.client", return_value=mock_client),
            pytest.raises(ClientError),
        ):
            storage.ensure_s3_bucket()