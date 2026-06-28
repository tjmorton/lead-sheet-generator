"""App logging config"""

import logging
import os
import sys
import warnings

# Root-level warning messages from dependencies that we can't silence
# by setting the library's own logger level (they call logging.warning()
# directly, which goes to the root logger).
# This is annoying - I'm not sure why dependecies would seriously write to a root logger
#   rather than their own.
# TODO: (tjm) Understand more about python logging conventions
_SUPPRESSED_ROOT_PATTERNS = (
    "Coremltools is not installed",
    "tflite-runtime is not installed",
)


class _SuppressRootPatterns(logging.Filter):
    """Filter out root-logger warnings matching known dependency noise."""

    def filter(self, record: logging.LogRecord) -> bool:
        if record.name == "root" and record.levelno >= logging.WARNING:
            return not any(p in record.msg for p in _SUPPRESSED_ROOT_PATTERNS)
        return True


def configure_logging() -> None:
    """Configure the root level app logging"""
    # Suppress noisy output from TensorFlow libraries
    # We should probably just add this to the .env.example and pass it via docker-compose
    # TODO: (tjm) set this via docker-compose
    os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")
    # Suppress onnxruntime C++ logs (device discovery warnings etc.)
    # This is separate from the Python-level onnxruntime logger.
    os.environ.setdefault("ORT_LOG_LEVEL", "FATAL")

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
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    # Attach filter to suppress dependency noise that uses the root logger
    for handler in logging.getLogger().handlers:
        handler.addFilter(_SuppressRootPatterns())

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
