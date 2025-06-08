import logging
import logging.handlers
import os
import sys

from app.utils.path_util import get_root_dir

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VIDEO_SOURCE_DIR = os.path.join(BASE_DIR, "temp_videos")

LOG_DIR = os.path.join(get_root_dir(), 'logs')
STDOUT_LOG_PATH = os.path.join(LOG_DIR, "stdout.log")
STDERR_LOG_PATH = os.path.join(LOG_DIR, "stderr.log")
LOG_FILE_PATH = os.path.join(LOG_DIR, 'app.log')

UPLOAD_DIR = os.path.join(get_root_dir(), 'temp', 'uploads')
MERGED_PDF_DIR = os.path.join(get_root_dir(), 'temp', 'merged_pdfs')
SECRET_KEY = 'app-secret-key'
os.makedirs(LOG_DIR, exist_ok=True)


def setup_logger():
    logger = logging.getLogger("flask_app")
    logger.setLevel(logging.INFO)

    if logger.handlers:
        return logger

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    file_handler = logging.handlers.TimedRotatingFileHandler(
        LOG_FILE_PATH, when='midnight', interval=1, backupCount=7
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger


logger = setup_logger()

sys.stdout = open(STDOUT_LOG_PATH, 'a')
sys.stderr = open(STDERR_LOG_PATH, 'a')
