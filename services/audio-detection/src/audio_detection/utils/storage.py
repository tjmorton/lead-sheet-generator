"""Utilites for S3 Storage"""

import logging

import boto3
from botocore.exceptions import ClientError

from .environment import get_environment

config = get_environment()
logger = logging.getLogger(__name__)


def ensure_s3_bucket() -> None:
    """Create S3 bucket if it doesn't exist.

    Raises
    ------
    Exception
        If bucket creation fails for reasons other than already existing
    """
    logger.info("Bootstrapping S3 bucket")

    # Get values from environment
    endpoint_url = config["aws_endpoint_url"]
    access_key_id = config["aws_access_key_id"]
    secret_access_key = config["aws_secret_access_key"]
    region = config["aws_region"]
    bucket_name = config["s3_bucket_name"]

    logger.debug("Using S3 bucket name %s", bucket_name)

    s3_client = boto3.client(
        "s3",
        endpoint_url=endpoint_url,
        aws_access_key_id=access_key_id,
        aws_secret_access_key=secret_access_key,
        region_name=region,
    )

    try:
        s3_client.head_bucket(Bucket=bucket_name)
        logger.debug("S3 bucket %s already exists", bucket_name)
    except ClientError as e:
        # If we've got a 404 back, create the bucket
        error_code = e.response["Error"]["Code"]
        if error_code == "404":
            logger.debug("S3 bucket doesn't exist, creating bucket...")
            try:
                s3_client.create_bucket(Bucket=bucket_name)
                logger.debug("S3 bucket created")
            except ClientError as create_error:
                logger.error("Failed to create S3 bucket, %s", create_error)
                raise
        else:
            logger.error("Failed to check for S3 bucket")
            raise

    logger.info("Finished bootstrapping S3 bucket")
