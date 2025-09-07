# logging_config.py
import logging
import sys
from logging.handlers import RotatingFileHandler
import os


def setup_logging(log_level=logging.INFO):
    # Create logs directory if it doesn't exist
    if not os.path.exists("logs"):
        os.makedirs("logs")

    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(log_level)
    
    # Create formatters with more detailed information
    console_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
    )
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s - %(message)s"
    )

    # Console Handler (stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File Handler (with rotation)
    file_handler = RotatingFileHandler(
        "logs/wallstreet_agent.log", maxBytes=10485760, backupCount=5  # 10MB
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # Set all loggers to DEBUG level
    for name in logging.root.manager.loggerDict:
        logging.getLogger(name).setLevel(log_level)

    # Log the logging configuration
    logger.debug("Logging configuration initialized with level: %s", logging.getLevelName(log_level))
    logger.debug("Console logging enabled")
    logger.debug("File logging enabled at logs/wallstreet_agent.log")

    # Disable uvicorn access logs
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
