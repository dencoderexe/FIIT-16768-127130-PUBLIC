from logging.handlers import TimedRotatingFileHandler

import os
import logging

def setup_logging():
    """
    configure application logging:

    - logs are written both to console and rotating log files

    - log files rotate everyday (midnight) with a retention of 7 days

    - refuce verbosity of Dash and Werkzeug internal logs
    """

    # ensure log dir exists
    os.makedirs(".logs", exist_ok=True)

    # set log format
    formatter = logging.Formatter(
        fmt="%(asctime)s.%(msecs)03d | %(levelname)s | %(threadName)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # file handler with daily rotation
    log_file_handler = TimedRotatingFileHandler(
        filename=".logs/app.log",
        when="midnight",    # rotation at midnight
        interval=1,         # every day
        backupCount=7,      # keep up to 7 log files
        encoding="utf-8",
    )

    log_file_handler.setFormatter(formatter)

    # console output handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # apply configuration
    logging.basicConfig(
        level=logging.INFO,
        handlers=[
            log_file_handler,
            console_handler,
        ],
        force=True, # override any existing configs
    )

    # reduce noise from external libs
    logging.getLogger("werkzeug").setLevel(logging.WARNING)
    logging.getLogger("dash").setLevel(logging.WARNING)
    logging.getLogger("dash.dash").setLevel(logging.WARNING)