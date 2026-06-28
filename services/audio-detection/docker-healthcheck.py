#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# Docker healthcheck script — NOT application code.
#
# Queries the RabbitMQ Management API for the queue's consumer count and
# exits 0 (healthy) when consumers > 0, meaning the audio-detection service
# is actively listening on the queue and ready to process messages.
#
# Used by Docker Compose's healthcheck on the audio-detection container to
# gate the test-harness startup — the harness won't send a message until the
# consumer is confirmed ready.
#
# Depends on these environment variables (already set via docker compose
# env_file):
#   RABBITMQ_HOST, RABBITMQ_USER, RABBITMQ_PASSWORD, RABBITMQ_QUEUE_NAME
# ---------------------------------------------------------------------------
import base64
import json
import os
import sys
import urllib.request


def main() -> None:
    user = os.environ["RABBITMQ_USER"]
    password = os.environ["RABBITMQ_PASSWORD"]
    host = os.environ["RABBITMQ_HOST"]
    queue = os.environ["RABBITMQ_QUEUE_NAME"]

    url = f"http://{host}:15672/api/queues/%2F/{queue}"
    creds = base64.b64encode(f"{user}:{password}".encode()).decode()

    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Basic {creds}")

    with urllib.request.urlopen(req) as response:
        data = json.load(response)

    sys.exit(0 if data.get("consumers", 0) > 0 else 1)


if __name__ == "__main__":
    main()
