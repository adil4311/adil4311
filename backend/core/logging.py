from __future__ import annotations

import os
import sys
from loguru import logger


def configure_logging(debug: bool) -> None:
    """Configure application logging with Loguru.

    Replaces default handlers and sets rotation.
    """

    logger.remove()
    log_level = "DEBUG" if debug else "INFO"
    logger.add(sys.stderr, level=log_level, enqueue=True, backtrace=False)

    os.makedirs("logs", exist_ok=True)
    logger.add(
        "logs/hyperai.log",
        level=log_level,
        rotation="10 MB",
        retention="10 days",
        compression="zip",
        enqueue=True,
    )