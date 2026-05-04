import logging
import sys
import os


def setup_logger():
    logger = logging.getLogger("api_copilot")

    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s"
    )

    # ========================
    # STDOUT (PRIMARY)
    # ========================
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    # ========================
    # FILE (SECONDARY)
    # ========================
    os.makedirs("logs", exist_ok=True)

    file_handler = logging.FileHandler("logs/app.log")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


logger = setup_logger()
