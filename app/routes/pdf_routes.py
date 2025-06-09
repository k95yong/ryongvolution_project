import os
import uuid
import shutil
from flask import Blueprint, request, render_template, redirect, url_for, session, send_file, current_app
from werkzeug.utils import secure_filename
from app.utils.log_util import logger
from app.utils.util import merge_jpgs_vertically_to_pdf

pdf_bp = Blueprint('pdf', __name__)

@pdf_bp.route("/image_to_pdf")
def image_to_pdf():
    return render_template("upload_images.html", message="Image to PDF")

@pdf_bp.route("/merge_to_pdf", methods=['POST'])
def merge_to_pdf():
    logger.info("/merge_to_pdf() called")
    files = request.files.getlist('image_files')
    if not files or files[0].filename == '':
        return "유효한 파일이 없습니다.", 400

    session_id = str(uuid.uuid4())
    target_dir = os.path.join(current_app.config['UPLOAD_DIR'], session_id)
    os.makedirs(target_dir)

    try:
        for file in files:
            filename = secure_filename(file.filename)
            file.save(os.path.join(target_dir, filename))

        pdf_filename = f"merged_{session_id}.pdf"
        pdf_path = merge_jpgs_vertically_to_pdf(target_dir, current_app.config['MERGED_PDF_DIR'], pdf_filename)

        if pdf_path and os.path.exists(pdf_path):
            session['pdf_to_download'] = os.path.basename(pdf_path)
            return redirect(url_for('.merge_success'))
        else:
            return render_template("error.html", message="PDF 파일 생성에 실패했습니다.")
    finally:
        shutil.rmtree(target_dir)

@pdf_bp.route("/merge_success")
def merge_success():
    pdf_filename = session.get('pdf_to_download')
    if not pdf_filename:
        return redirect(url_for('.image_to_pdf'))
    return render_template("success.html", download_url=url_for('.download_file', filename=pdf_filename))

@pdf_bp.route("/download/<filename>")
def download_file(filename):
    file_path = os.path.join(current_app.config['MERGED_PDF_DIR'], filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    return "파일을 찾을 수 없습니다.", 404

@pdf_bp.route("/download_pdf")
def download_pdf():
    p = session.get("params")
    pdf_path = p.get("pdf_path")
    if pdf_path and os.path.exists(pdf_path):
        return render_template("success.html", pdf_path=pdf_path)
    return render_template("error.html", message="PDF 파일이 존재하지 않습니다.")