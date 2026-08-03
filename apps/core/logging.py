"""Centralized logging module for A.RISK ERM."""

import logging
from typing import Optional

# Get logger for the apps module
def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get a logger instance.

    Args:
        name: Logger name (usually __name__ from the calling module)

    Returns:
        Configured logger instance
    """
    if name is None:
        name = __name__
    return logging.getLogger(name)


# Common loggers for different purposes
logger = get_logger('apps')
api_logger = get_logger('apps.api')
db_logger = get_logger('apps.database')
error_logger = get_logger('apps.errors')
audit_logger = get_logger('apps.audit')


# Convenience functions for common logging patterns

def log_info(message: str, logger_name: str = 'apps', **kwargs):
    """Log info message."""
    logger = get_logger(logger_name)
    logger.info(message, extra=kwargs)


def log_error(message: str, logger_name: str = 'apps', exc_info: bool = False, **kwargs):
    """Log error message."""
    logger = get_logger(logger_name)
    logger.error(message, exc_info=exc_info, extra=kwargs)


def log_warning(message: str, logger_name: str = 'apps', **kwargs):
    """Log warning message."""
    logger = get_logger(logger_name)
    logger.warning(message, extra=kwargs)


def log_debug(message: str, logger_name: str = 'apps', **kwargs):
    """Log debug message."""
    logger = get_logger(logger_name)
    logger.debug(message, extra=kwargs)
