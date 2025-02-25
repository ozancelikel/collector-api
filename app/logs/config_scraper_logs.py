import logging
import os
import sys
from pathlib import Path


log_dir = Path(__file__).resolve().parent

scraper_logger = logging.getLogger("scraper")
scraper_logger.setLevel(logging.INFO)

log_file_path = os.path.join(log_dir, 'scraper.log')
print(log_file_path)
scraper_handler = logging.FileHandler(log_file_path, encoding='utf-8')
scraper_handler.setLevel(logging.INFO)

formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
scraper_handler.setFormatter(formatter)


if not scraper_logger.hasHandlers():
    scraper_logger.addHandler(scraper_handler)

scraper_logger.info("############## !!! SCRAPER RESTARTED !!! ##############")