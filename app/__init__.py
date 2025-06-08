from flask import Flask
from app.routes.youtube_script_routes import youtube_script_bp
from app.routes.pdf_routes import pdf_bp
from app.routes.common_routes import common_bp
from app.utils.path_util import get_root_dir
import os

UPLOAD_DIR = os.path.join(get_root_dir(), 'temp', 'uploads')
MERGED_PDF_DIR = os.path.join(get_root_dir(), 'temp', 'merged_pdfs')
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(MERGED_PDF_DIR, exist_ok=True)


def create_app():
    app = Flask(__name__,
                template_folder=os.path.join(get_root_dir(), 'app', 'templates'),
                static_folder=os.path.join(get_root_dir(), 'static'))
    app.secret_key = 'app-secret-key'

    app.config['UPLOAD_DIR'] = UPLOAD_DIR
    app.config['MERGED_PDF_DIR'] = MERGED_PDF_DIR

    app.register_blueprint(common_bp)
    app.register_blueprint(youtube_script_bp, url_prefix='/youtube_script')
    app.register_blueprint(pdf_bp)

    return app
