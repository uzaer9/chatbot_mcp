import logging
import sys
from loguru import logger
from app.config import config

# Remove default loguru logger
logger.remove()

# Add console logger with custom format
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level=config.LOG_LEVEL
)

# Add file logger if needed
if config.DEBUG_MODE:
    logger.add(
        "logs/app.log",
        rotation="1 day",
        retention="7 days",
        level=config.LOG_LEVEL,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
    )

def get_logger(name: str):
    """Get a logger instance for a specific module"""
    return logger.bind(name=name)