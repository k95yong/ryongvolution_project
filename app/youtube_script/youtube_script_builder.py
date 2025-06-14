import os

from app.utils.google_uploader import upload_to_drive
from app.utils.log_util import logger
from app.utils.path_util import get_root_dir
from app.utils.util import download_youtube, merge_jpgs_vertically_to_pdf, capture_video_frame, \
    remove_duplicate_img, show_capture_guide_web, apply_bar_numbering_in_dir, \
    extract_video_id


class YoutubeScriptBuilder:
    def __init__(self, title, url):
        self.title = title
        self.url = url

        self.output_root_dir = os.path.join(get_root_dir(), 'temp')
        self.download_dir = os.path.join(get_root_dir(), 'temp', title)
        self.script_dir = os.path.join(get_root_dir(), 'temp', title, "captured_scripts")
        self.pdf_dir = os.path.join(get_root_dir(), 'temp', title, "pdfs")
        os.makedirs(self.download_dir, exist_ok=True)
        self.video_path = os.path.join(str(self.output_root_dir), f"{title}_{extract_video_id(url)}")
        self.pdf_path = os.path.join(str(self.pdf_dir), "{}.pdf".format(title))
        self.start_time = None
        self.end_time = None

    def set_output_root_dir(self, output_root_dir):
        self.output_root_dir = output_root_dir

    def set_time_range(self, start_time=None, end_time=None):
        self.start_time = start_time
        self.end_time = end_time

    def download_youtube(self):
        return download_youtube(self.url, start_time=self.start_time, end_time=self.end_time,
                                output_path=self.video_path)

    def capture_video_frame(self, y_start=60, y_end=100, interval_sec=4):
        if interval_sec is None:
            interval_sec = interval_sec
        logger.info(f"[capture_video_frame]: {self.video_path}")
        capture_video_frame(f"{self.video_path}.mp4", self.script_dir, interval_sec, y_start=y_start, y_end=y_end)

    def remove_duplicate_imgs(self):
        remove_duplicate_img(self.script_dir)

    def apply_bar_numbering_in_dir(self):
        apply_bar_numbering_in_dir(self.script_dir, 4)

    def merge_jpgs_to_pdf(self):
        return merge_jpgs_vertically_to_pdf(self.script_dir, self.pdf_dir, self.title)

    def show_capture_guide_web(self, guide_path=os.path.join(get_root_dir(), "static", "img", "guide.jpg")):
        show_capture_guide_web(f"{self.video_path}.mp4", guide_path)

    def upload_pdf_to_google_dirve(self, folder_id=None):
        if folder_id is None:
            folder_id = "1Gi7Y3GAV2t1tTFnGM5KMYN35eAd1D2Wi"
        credentials = os.path.join(str(self.output_root_dir), "config", "google_credentials.json")
        upload_to_drive(
            file_path=self.pdf_path,
            folder_id=folder_id,
            credentials=credentials
        )
