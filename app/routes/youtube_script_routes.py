import os
from flask import Blueprint, request, redirect, url_for, session, render_template, send_file

from app.utils.log_util import logger
from app.youtube_script.youtube_script_builder import YoutubeScriptBuilder
from app.utils.path_util import get_root_dir

youtube_script_bp = Blueprint('youtube_script', __name__)


@youtube_script_bp.route("/", methods=["GET", "POST"])
def youtube_script():
    if request.method == "POST":
        title = request.form["title"]
        url = request.form["url"]
        start_time = request.form.get("start_time") or None
        end_time = request.form.get("end_time") or None
        bpm = request.form.get("bpm", type=int) or 100
        output_root_dir = request.form.get("output_root_dir") or os.path.join(os.path.expanduser("~"), "Downloads")

        gh = YoutubeScriptBuilder(title, url, output_root_dir)
        gh.set_bpm(bpm)
        gh.start_time = start_time
        gh.end_time = end_time
        gh.set_time_range(start_time, end_time)
        gh.video_path = gh.download_youtube()
        logger.info(f"[캐시 결과] {gh.video_path}")
        gh.show_capture_guide_web(guide_path=os.path.join(get_root_dir(), "static", "img", "guide.jpg"))

        session["params"] = {
            "title": title, "url": url,
            "start_time": start_time, "end_time": end_time,
            "bpm": bpm, "output_root_dir": output_root_dir,
            "video_path": gh.video_path,
        }

        return redirect(url_for(".confirm_y"))

    return render_template("youtube_script_info.html")


@youtube_script_bp.route("/confirm_y", methods=["GET", "POST"])
def confirm_y():
    return render_template("confirm_y.html", guide_img=url_for('static', filename='img/guide.jpg'))


@youtube_script_bp.route("/start_confirm_y", methods=["POST"])
def start_confirm_y():
    session["y_start"] = request.form["y_start"]
    session["y_end"] = request.form["y_end"]
    return render_template("loading_pdf.html")


@youtube_script_bp.route("/process_confirm_y")
def process_confirm_y():
    y_start = int(session["y_start"])
    y_end = int(session["y_end"])
    p = session["params"]
    gh = YoutubeScriptBuilder(p["title"], p["url"], p["output_root_dir"])
    gh.video_path = p["video_path"]
    logger.info(f"[Confirm_y Video Path] {gh.video_path}")

    gh.set_bpm(p["bpm"])
    gh.set_time_range(p["start_time"], p["end_time"])
    gh.capture_video_frame(y_start, y_end)
    gh.remove_duplicate_imgs()
    gh.apply_bar_numbering_in_dir()
    pdf_path = gh.merge_jpgs_to_pdf()
    p["pdf_path"] = pdf_path
    session["params"] = p
    return redirect(url_for("youtube_script.download_pdf_file"))


@youtube_script_bp.route("/download_pdf_file")
def download_pdf_file():
    p = session.get("params")
    pdf_path = p.get("pdf_path")
    if pdf_path and os.path.exists(pdf_path):
        return render_template("success.html", download_url=url_for("youtube_script.download_pdf_file_raw"))
    return render_template("error.html", message="파일이 존재하지 않습니다.")


@youtube_script_bp.route("/download_pdf_file_raw")
def download_pdf_file_raw():
    p = session.get("params")
    pdf_path = p.get("pdf_path")
    if pdf_path and os.path.exists(pdf_path):
        return send_file(pdf_path, as_attachment=True, download_name=f"{p.get('title')}.pdf",
                         mimetype="application/pdf")
    return render_template("error.html", message="파일이 존재하지 않습니다.")
