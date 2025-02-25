import logging
import os
import sys
from pathlib import Path


log_dir = Path(__file__).resolve().parent

server_logger = logging.getLogger("server")
server_logger.setLevel(logging.INFO)

log_file_path = os.path.join(log_dir, 'server.log')

server_handler = logging.FileHandler(log_file_path, encoding='utf-8')
server_handler.setLevel(logging.INFO)

formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
server_handler.setFormatter(formatter)

if not server_logger.hasHandlers():
    server_logger.addHandler(server_handler)
