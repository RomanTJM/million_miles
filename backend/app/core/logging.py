import logging
import sys
from logging.handlers import RotatingFileHandler

logger = logging.getLogger("app")
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(formatter)

file_handler = RotatingFileHandler(
    'logs/app.log',
    maxBytes=10485760,
    backupCount=10
)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)

scraper_logger = logging.getLogger("scraper")
scraper_logger.setLevel(logging.INFO)
scraper_file_handler = RotatingFileHandler(
    'logs/scraper.log',
    maxBytes=10485760,
    backupCount=5
)
scraper_file_handler.setFormatter(formatter)
scraper_logger.addHandler(scraper_file_handler)


def get_logger(name: str = "app") -> logging.Logger:
    return logging.getLogger(name)
