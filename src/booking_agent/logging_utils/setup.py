from logging.config import dictConfig
from .config import LOGGING_CONFIG

def configure_logging():
    dictConfig(LOGGING_CONFIG)
