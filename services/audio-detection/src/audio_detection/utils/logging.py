"""App logging config"""

import logging
import os
import sys
import warnings


def configure_logging() -> None:
    """Configure the root level app logging"""
    # Suppress noisy output from TensorFlow libraries
    # We should probably just add this to the .env.example and pass it via docker-compose
    # TODO: (tjm) set this via docker-compose
    os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")

    # Suppress deprecation wartnings from crema's use of pkg_resources / librosa API
    warnings.filterwarnings("ignore", category=FutureWarning, module="crema")
    warnings.filterwarnings("ignore", message="pkg_resources is deprecated")

    # Configure application logging at the root level
    #   CRITICAL = 50
    #   FATAL = CRITICAL
    #   ERROR = 40
    #   WARNING = 30
    #   WARN = WARNING
    #   INFO = 20
    #   DEBUG = 10
    #   NOTSET = 0
    # TODO: (tjm) Let's set this by get_environment
    logging.basicConfig(
        level=logging.DEBUG,
        # log message format TODO: (tjm) we should have this as JSON in prod (or maybe add otel?)
        format="%(asctime)s - %(name)s - %(levelname) - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    # Dependencies by convention will call logging.getLogger(<dependencyname>)
    #   So for a bunch of dependency logs we want to want to typically silence we'll loop over
    #   a list of libraries and set their log levels
    for _lib in (
        "tensorflow",
        "absl",
        "h5py",
        "onnxruntime",
        "basic_pitch",
        "urllib",
        "botocore",
        "boto3",
        "pika",
    ):
        logging.getLogger(_lib).setLevel(logging.ERROR)