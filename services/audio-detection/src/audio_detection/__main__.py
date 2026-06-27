"""Entry point for audio-detection queue processing"""

import logging

# NOTE: (tjm) Temporarily removing
# from .messaging import start_listener
# from .utils.bootstrap import bootstrap_infrastructure
# In general, I don't want to access env vars via os.environ
#   I'd like some indirection between that and our application code
#   Helpful for things like env var validation, and early fail if miscongifured
from .utils import configure_logging, get_environment

configure_logging()

logger = logging.getLogger(__name__)

def main():
    logger.info("testing 123")

if __name__ == "__main__":
    main()