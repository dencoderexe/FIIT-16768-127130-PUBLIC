from logging.handlers import TimedRotatingFileHandler

import os
import logging

def setup_logging():
    os.makedirs(".logs", exist_ok=True)

    formatter = logging.Formatter(
        fmt="%(asctime)s.%(msecs)03d | %(levelname)s | %(threadName)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    log_file_handler = TimedRotatingFileHandler(
        filename=".logs/app.log",
        when="midnight",   # rotation at midnight
        interval=1,        # every day
        backupCount=7,      # keep up to 7 files
        encoding="utf-8",
    )

    log_file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logging.basicConfig(
        level=logging.INFO,
        handlers=[
            log_file_handler,
            console_handler,
        ],
        force=True,
    )

    logging.getLogger("werkzeug").setLevel(logging.WARNING)
    logging.getLogger("dash").setLevel(logging.WARNING)
    logging.getLogger("dash.dash").setLevel(logging.WARNING)