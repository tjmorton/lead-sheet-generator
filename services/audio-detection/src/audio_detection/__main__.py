"""Entry point for audio-detection queue processing"""

import logging

from .utils import configure_logging

# NOTE: (tjm) Temporarily removing
# from .messaging import start_listener
# from .utils.bootstrap import bootstrap_infrastructure
# In general, I don't want to access env vars via os.environ
#   I'd like some indirection between that and our application code
#   Helpful for things like env var validation, and early fail if miscongifured

configure_logging()

logger = logging.getLogger(__name__)


def main():
    # We have to lazy import this. One of the imports under ensure_ml_models
    # adds a StreamHandler <stderr> to Python's root logger during its own import.
    # After that, logging.basicConfig() fails because the root logger already has
    # handlers.
    # TODO: (tjm) Understand this more - I must be missing something 
    from .utils.model_cache import ensure_ml_models

    ensure_ml_models()
    logger.info("testing 123")


if __name__ == "__main__":
    main()
