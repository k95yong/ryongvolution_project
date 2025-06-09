import os

from app.utils.path_util import get_root_dir

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VIDEO_SOURCE_DIR = os.path.join(BASE_DIR, "temp_videos")

LOG_DIR = os.path.join(get_root_dir(), 'logs')
LOG_FILE_PATH = os.path.join(LOG_DIR, 'app.log')

UPLOAD_DIR = os.path.join(get_root_dir(), 'temp', 'uploads')
MERGED_PDF_DIR = os.path.join(get_root_dir(), 'temp', 'merged_pdfs')
SECRET_KEY = 'app-secret-key'
os.makedirs(LOG_DIR, exist_ok=True)

