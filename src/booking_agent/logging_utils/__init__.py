import logging
from .setup import configure_logging

_logger_cache = {}

def get_logger(name: str = "calendar_booking_agent") -> logging.Logger:
    if not _logger_cache.get(name):
        configure_logging()
        _logger_cache[name] = logging.getLogger(name)
    return _logger_cache[name]
