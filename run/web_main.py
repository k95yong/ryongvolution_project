import os
import shutil
import tempfile

from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask import send_file
from werkzeug.utils import secure_filename

from app.utils.path_util import get_root_dir
from app.utils.util import merge_jpgs_vertically_to_pdf
from app.youtube_script.youtube_script_builder import YoutubeScriptBuilder

app = Flask(__name__,
            template_folder=os.path.join(get_root_dir(), 'app', 'templates'),
            static_folder=os.path.join(get_root_dir(), 'static'))
app.secret_key = "secret"  # 세션용 키
UPLOAD_TEMP_DIR = tempfile.gettempdir()

@app.route("/health_check")
def health_check():
    return jsonify(status="ok"), 200

@app.route('/')
def index_redirect():
    return redirect(url_for('home'))

@app.route("/home", methods=["GET", "POST"])
def home():
    return render_template("home.html")

@app.route("/youtube_script", methods=["GET", "POST"])
def youtube_script():
    if request.method == "POST":
        title = request.form["title"]
        url = request.form["url"]
        start_time = request.form.get("start_time") or None
        end_time = request.form.get("end_time") or None
        bpm = request.form.get("bpm", type=int) or 100
        output_root_dir = request.form.get("output_root_dir")

        if not output_root_dir or output_root_dir.strip() == "":
            output_root_dir = os.path.join(os.path.expanduser("~"), "Downloads")

        gh = YoutubeScriptBuilder(title, url, output_root_dir)
        gh.set_bpm(bpm)
        gh.start_time = start_time
        gh.end_time = end_time
        gh.set_time_range(start_time, end_time)

        gh.download_youtube()
        gh.show_capture_guide_web(guide_path=os.path.join(get_root_dir(), "static", "guide.jpg"))

        session["params"] = {
            "title": title,
            "url": url,
            "start_time": start_time,
            "end_time": end_time,
            "bpm": bpm,
            "output_root_dir": output_root_dir,
        }

        return redirect(url_for("confirm_y"))

    return render_template("youtube_script_info.html")


@app.route("/youtube_script/confirm_y", methods=["GET", "POST"])
def confirm_y():
    if request.method == "POST":
        y_start = int(request.form["y_start"])
        y_end = int(request.form["y_end"])

        p = session.get("params")
        output_path = p['output_root_dir']
        gh = YoutubeScriptBuilder(p["title"], p["url"], output_path)
        gh.set_bpm(p["bpm"])
        gh.start_time = p["start_time"]
        gh.end_time = p["end_time"]
        gh.set_time_range(p["start_time"], p["end_time"])

        gh.capture_video_frame(y_start, y_end)
        gh.remove_duplicate_imgs()
        pdf_path = gh.merge_jpgs_to_pdf()
        # gh.upload_pdf_to_google_dirve()

        params = session.get("params", {})
        params["pdf_path"] = pdf_path
        session["params"] = params
        return redirect(url_for("download_pdf"))

    return render_template("confirm_y.html", guide_img=url_for('static', filename='guide.jpg'))


@app.route("/youtube_script/start_confirm_y", methods=["POST"])
def start_confirm_y():
    session["y_start"] = request.form["y_start"]
    session["y_end"] = request.form["y_end"]
    return render_template("loading_pdf.html")


@app.route("/youtube_script/process_confirm_y")
def process_confirm_y():
    y_start = int(session["y_start"])
    y_end = int(session["y_end"])
    p = session["params"]
    gh = YoutubeScriptBuilder(p["title"], p["url"], p["output_root_dir"])
    gh.set_bpm(p["bpm"])
    gh.set_time_range(p["start_time"], p["end_time"])

    gh.capture_video_frame(y_start, y_end)
    gh.remove_duplicate_imgs()
    gh.apply_bar_numbering_in_dir()
    pdf_path = gh.merge_jpgs_to_pdf()

    params = session.get("params")
    params["pdf_path"] = pdf_path
    session["params"] = params

    return redirect(url_for("download_pdf"))


@app.route("/youtube_script/download_pdf")
def download_pdf():
    p = session.get("params")
    pdf_path = p.get("pdf_path")
    if pdf_path and os.path.exists(pdf_path):
        return render_template("success.html", pdf_path=pdf_path)
    else:
        return render_template("error.html", message="PDF 파일이 존재하지 않습니다.")


@app.route("/youtube_script/download_pdf_file")
def download_pdf_file():
    p = session.get("params")
    pdf_path = p.get("pdf_path")
    if pdf_path and os.path.exists(pdf_path):
        return send_file(pdf_path, as_attachment=True)
    else:
        return render_template("error.html", message="파일이 존재하지 않습니다.")

@app.route("/image_to_pdf")
def image_to_pdf():
    print("image_to_pdf()")
    return render_template("upload_images.html", message="Image to PDF")

@app.route("/merge_to_pdf", methods=['POST'])
def merge_to_pdf():
    print("/merge_to_pdf()")
    target_dir = None
    pdf_path = None
    try:
        if 'image_files' not in request.files:
            return "파일이 없습니다.", 400

        files = request.files.getlist('image_files')
        if not files or files[0].filename == '':
            return "업로드할 유효한 파일이 없습니다.", 400

        target_dir = tempfile.mkdtemp(dir=UPLOAD_TEMP_DIR, prefix='pdf_source_images_')
        print(target_dir)

        uploaded_count = 0
        for file in files:
            if file.filename:
                filename = secure_filename(file.filename)
                file_path = os.path.join(target_dir, filename)
                file.save(file_path)
                uploaded_count += 1
                print(f"파일 저장됨: {file_path}")

        pdf_path = merge_jpgs_vertically_to_pdf(target_dir, UPLOAD_TEMP_DIR, 'pdf_file')
        if pdf_path and os.path.exists(pdf_path):
            return send_file(pdf_path, as_attachment=True)
        else:
            return render_template("error.html", message="파일이 존재하지 않습니다.")
    finally:
        if pdf_path and target_dir and os.path.exists(target_dir):
            try:
                shutil.rmtree(target_dir)
                print(f"임시 디렉토리 정리 완료: {target_dir}")
            except Exception as e:
                print(f"임시 디렉토리 정리 중 오류 발생: {e}")


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)

