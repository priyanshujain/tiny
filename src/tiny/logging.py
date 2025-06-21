"""Logging system for tiny CLI application."""

import logging
from datetime import datetime
from pathlib import Path
from typing import Optional


class LoggingContext:
    """Context manager to handle logging setup and cleanup."""

    def __init__(self, log_level: str = "INFO"):
        self.log_level = log_level.upper()
        self.logger = None
        self.log_file_path = None

    def __enter__(self):
        self.logger, self.log_file_path = setup_logging(self.log_level)
        return self.logger

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.logger:
            for handler in self.logger.handlers[:]:
                handler.close()
                self.logger.removeHandler(handler)


def setup_logging(log_level: str = "INFO") -> tuple[logging.Logger, Path]:
    """
    Set up logging system with file output and console suppression.

    Returns:
        tuple: (logger instance, log file path)
    """
    log_dir = Path.home() / ".tiny" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    today = datetime.now().strftime("%Y%m%d")
    log_file_path = log_dir / f"{today}.log"

    logger = logging.getLogger("tiny")
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    # Remove existing handlers to avoid duplicates
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # File handler captures all logs, console handler only shows errors
    file_handler = logging.FileHandler(log_file_path)
    file_handler.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.ERROR)

    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    # Prevent propagation to avoid duplicate logs
    logger.propagate = False

    return logger, log_file_path


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get a logger instance for the specified module.

    Args:
        name: Logger name, defaults to tiny if not provided

    Returns:
        Logger instance
    """
    if name:
        return logging.getLogger(f"tiny.{name}")
    return logging.getLogger("tiny")
