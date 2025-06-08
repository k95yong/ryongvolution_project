import subprocess

import numpy as np
import yt_dlp
from skimage.metrics import structural_similarity as ssim

from app.utils.cache_util import add_video_to_cache, cleanup_cache, load_video_cache
from app.utils.path_util import get_root_dir


def format_youtube_url(input_str):
    if input_str.startswith("http://") or input_str.startswith("https://"):
        return input_str
    else:
        return f"https://www.youtube.com/watch?v={input_str}"


def download_youtube(url, output_path='downloaded_video.mp4', start_time=None, end_time=None):
    url = format_youtube_url(url)
    start_time = convert_to_hms(start_time)
    end_time = convert_to_hms(end_time)

    cached_path = find_cached_video(url, start_time, end_time)
    if cached_path:
        print(f"✅ 캐시된 영상 있음: {cached_path} → 다운로드 생략")
        return cached_path

    my_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Whale/4.31.304.16 Safari/537.36"

    temp_path = 'temp_downloaded_video.mp4'
    ydl_opts = {
        'format': 'bestvideo[height<=480]+bestaudio/best[height<=480]',
        'http_headers': {
            'User-Agent': my_user_agent
        },
        'format': 'bestvideo+bestaudio/best',  # 영상 + 오디오
        'merge_output_format': 'mp4',  # mp4로 병합 저장
        'outtmpl': temp_path,  # 저장 경로
        'quiet': False,  # 로그 출력
        'cookiefile': os.path.join(get_root_dir(), 'config', 'cookies.txt')
    }
    if not output_path.endswith('.mp4'):
        output_path = output_path + '.mp4'

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    if start_time or end_time:
        cmd = ['ffmpeg', '-y']

        if start_time:
            cmd += ['-ss', str(start_time)]

        cmd += ['-i', temp_path]

        if end_time:
            cmd += ['-to', str(end_time)]

        cmd += ['-c', 'copy', output_path]

        subprocess.run(cmd, check=True)
        os.remove(temp_path)
    else:
        import shutil
        shutil.move(temp_path, output_path)

    add_video_to_cache(url, start_time, end_time, output_path)
    cleanup_cache(max_size_mb=5000)
    print(f"📝 캐시에 추가됨: {output_path}")
    return output_path


def convert_to_hms(timestr):
    if timestr and ":" in timestr:
        parts = timestr.split(":")
        if len(parts) == 2:
            return f"00:{parts[0].zfill(2)}:{parts[1].zfill(2)}"
    return timestr  # 그대로 반환하거나 예외처리


def find_cached_video(url, start_time, end_time):
    cache = load_video_cache()
    for entry in cache:
        if (
                entry["url"] == url and
                entry["start_time"] == start_time and
                entry["end_time"] == end_time and
                os.path.exists(entry["video_path"])
        ):
            return entry["video_path"]
    return None


def reset_directory(dir_path):
    if os.path.exists(dir_path):
        shutil.rmtree(dir_path)
    os.makedirs(dir_path)


import re


def extract_video_id(url):
    patterns = [
        r"(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([^&]+)",
        r"(?:https?://)?youtu\.be/([^?&]+)",
        r"(?:https?://)?(?:www\.)?youtube\.com/shorts/([^?&]+)",
        r"(?:https?://)?(?:www\.)?youtube\.com/embed/([^?&]+)",
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)

    return url


def create_lyrics_template(directory, filename="lyrics_template.txt"):
    file_path = os.path.join(directory, filename)
    if os.path.exists(file_path):
        print(f"이미 파일이 존재합니다: {file_path}")
        return file_path

    with open(file_path, "w", encoding="utf-8") as f:
        f.write("# 여기에 가사를 줄 단위로 입력하세요.\n")

    print(f"가사 템플릿 파일 생성 완료: {file_path}")
    return file_path


def get_video_duration(video_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("영상 열기 실패")
        return None

    fps = cap.get(cv2.CAP_PROP_FPS)  # 초당 프레임 수
    frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)  # 전체 프레임 수
    duration_sec = frame_count / fps  # 총 길이 (초)
    cap.release()

    return duration_sec


def show_capture_guide(video_path):
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print("비디오 열기 실패")
        return

    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    middle_frame_idx = total_frames // 2
    cap.set(cv2.CAP_PROP_POS_FRAMES, middle_frame_idx)
    ret, frame = cap.read()

    if ret:
        for i in range(5, 100, 5):
            y = int(height * (i / 100))
            cv2.line(frame, (0, y), (width, y), (0, 255, 0), 1)
            cv2.putText(frame, f"{i}%", (10, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 1)

        cv2.imshow('Guide Frame', frame)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    else:
        print("가이드 프레임 읽기 실패")

    cap.release()
    return


def show_capture_guide_web(video_path, guide_img_path):
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print("비디오 열기 실패")
        return None

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    middle_frame_idx = total_frames // 2
    cap.set(cv2.CAP_PROP_POS_FRAMES, middle_frame_idx)
    ret, frame = cap.read()

    if ret:
        # 라인과 텍스트 추가
        for i in range(10, 100, 10):
            y = int(height * (i / 100))
            cv2.line(frame, (0, y), (width, y), (0, 255, 0), 1)
            cv2.putText(frame, f"{i}%", (10, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

        # 저장 경로
        cv2.imwrite(guide_img_path, frame)
        print(f"가이드 이미지 저장 완료: {guide_img_path}")
        cap.release()
        return guide_img_path
    else:
        print("가이드 프레임 읽기 실패")
        cap.release()
        return None



import cv2
import tempfile


def seconds_to_timestamp(seconds):
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:02d}-{secs:02d}"


def format_bar_range(index, bars_per_image=4):
    start_bar = index * bars_per_image + 1
    end_bar = start_bar + bars_per_image - 1
    return f"{start_bar}-{end_bar}"


import shutil


def prepare_directory(output_dir, lyrics_filename="lyrics_template.txt"):
    os.makedirs(output_dir, exist_ok=True)

    lyrics_path = os.path.join(output_dir, lyrics_filename)

    if not os.path.exists(lyrics_path):
        with open(lyrics_path, "w", encoding="utf-8") as f:
            f.write("# 여기에 가사를 입력하세요.\n")
        print(f"{lyrics_filename} 생성 완료: {lyrics_path}")

    for f in os.listdir(output_dir):
        if f != lyrics_filename:
            path = os.path.join(output_dir, f)
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)


def capture_video_frame(video_path, output_dir, interval_sec=5, y_start=60, y_end=100, bars_per_image=4):
    prepare_directory(output_dir)

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("비디오 열기 실패")
        return []

    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_interval = int(fps * interval_sec)

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    crop_start_y = int(height * (y_start / 100))
    crop_end_y = int(height * (y_end / 100))
    if crop_start_y > crop_end_y:
        print("캡처 영역을 올바르게 지정하세요.")
        return []

    frame_idx = 0
    saved_files = []
    image_count = 0

    while frame_idx < total_frames:
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        ret, frame = cap.read()
        if not ret:
            break

        crop_image = frame[crop_start_y:crop_end_y, :]
        gray_image = cv2.cvtColor(crop_image, cv2.COLOR_BGR2GRAY)

        timestamp = seconds_to_timestamp(frame_idx / fps)
        filename = f"time_{timestamp}.jpg"

        temp_dir = tempfile.gettempdir()
        temp_save_path = os.path.join(temp_dir, f"temp_{filename}")

        success = cv2.imwrite(temp_save_path, gray_image)
        if success:
            final_save_path = os.path.join(output_dir, filename)
            shutil.move(temp_save_path, final_save_path)
            print(f"Saved {final_save_path}")
            saved_files.append(final_save_path)
        else:
            print(f"Failed to save {temp_save_path}")

        print(f"crop size: {gray_image.shape}")
        frame_idx += frame_interval
        image_count += 1

    cap.release()
    return saved_files


import os
from PIL import Image
from PyPDF2 import PdfWriter, PdfReader


def merge_jpgs_vertically_to_pdf(image_dir, output_pdf_path, pdf_title, dpi=300):
    images = [os.path.join(image_dir, f) for f in sorted(os.listdir(image_dir)) if f.lower().endswith('.jpg')]
    if not images:
        print("jpg 파일이 없습니다.")
        return None

    os.makedirs(output_pdf_path, exist_ok=True)
    pdf_file_path = os.path.join(output_pdf_path, f"{pdf_title}.pdf")
    output_pdf = PdfWriter()

    a4_width_px = int(595 * dpi / 72)
    a4_height_px = int(842 * dpi / 72)

    page_number = 1
    current_canvas = Image.new('RGB', (a4_width_px, a4_height_px), color=(255, 255, 255))
    y_offset = 0

    for img_path in images:
        img = Image.open(img_path).convert('RGB')
        img_ratio = img.width / img.height
        target_width = a4_width_px
        target_height = int(target_width / img_ratio)

        if y_offset + target_height > a4_height_px:
            temp_pdf_path = os.path.join(output_pdf_path, f"temp_page_{page_number}.pdf")
            current_canvas.save(temp_pdf_path, "PDF", resolution=dpi)
            temp_reader = PdfReader(temp_pdf_path)
            output_pdf.add_page(temp_reader.pages[0])
            os.remove(temp_pdf_path)
            page_number += 1

            current_canvas = Image.new('RGB', (a4_width_px, a4_height_px), color=(255, 255, 255))
            y_offset = 0

        resized_img = img.resize((target_width, target_height))
        current_canvas.paste(resized_img, (0, y_offset))
        y_offset += target_height

    if y_offset > 0:
        temp_pdf_path = os.path.join(output_pdf_path, f"temp_page_{page_number}.pdf")
        current_canvas.save(temp_pdf_path, "PDF", resolution=dpi)
        temp_reader = PdfReader(temp_pdf_path)
        output_pdf.add_page(temp_reader.pages[0])
        os.remove(temp_pdf_path)

    with open(pdf_file_path, 'wb') as f:
        output_pdf.write(f)

    print(f"PDF로 저장 완료: {pdf_file_path}")
    return pdf_file_path


def calculate_bar_duration(bpm, note_info="4/4"):
    """
    bpm: 분당 비트 수 (예: 120)
    note_info: 문자열 '4/4' 또는 튜플 (4, 4)
    """
    if isinstance(note_info, str):
        parts = note_info.split('/')
        if len(parts) != 2:
            raise ValueError("note_info 문자열은 반드시 '숫자/숫자' 형태여야 합니다.")
        note_value = int(parts[0])
        beat_count = int(parts[1])
    else:
        note_value, beat_count = note_info

    # 한 note_value당 걸리는 시간 계산
    seconds_per_note = (60 / bpm) * (4 / note_value)

    # 마디 하나 시간 = (note 시간) x (개수)
    bar_duration = seconds_per_note * beat_count

    return bar_duration


import fitz  # pip install pymupdf


def set_pdf_title(pdf_path, title):
    doc = fitz.open(pdf_path)
    if not title.endwith(".pdf"):
        title = title + ".pdf"
    doc.set_metadata({"title": title})
    doc.saveIncr()
    doc.close()


def remove_duplicate_img(image_dir):
    images = [os.path.join(image_dir, f) for f in sorted(os.listdir(image_dir)) if f.lower().endswith('.jpg')]
    dup_dir = os.path.join(image_dir, "duplicates")
    os.makedirs(dup_dir, exist_ok=True)
    prev_img = None
    for img_path in images:
        with open(img_path, 'rb') as f:
            data = f.read()
        img_array = np.asarray(bytearray(data), dtype=np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_GRAYSCALE)
        if prev_img is None:
            prev_img = img
        else:
            if is_same_sheet(prev_img, img):
                shutil.move(img_path, os.path.join(dup_dir, os.path.basename(img_path)))
            prev_img = img


def apply_bar_numbering_in_dir(image_dir, bars_per_image=4):
    images = [os.path.join(image_dir, f) for f in sorted(os.listdir(image_dir)) if f.lower().endswith('.jpg')]
    renamed_list = []
    for index, old_path in enumerate(images):
        dir_name, old_filename = os.path.split(old_path)
        name_part, ext = os.path.splitext(old_filename)

        start_bar = index * bars_per_image + 1
        end_bar = start_bar + bars_per_image - 1

        new_filename = f"{name_part}_section_{start_bar}-{end_bar}{ext}"
        new_path = os.path.join(dir_name, new_filename)

        os.rename(old_path, new_path)
        renamed_list.append(new_path)

    return renamed_list


def quick_difference(img1, img2, resize_dim=(64, 64), diff_threshold=30):
    """
    이미지 크기 축소 후 절대 차이 평균으로 빠른 필터링
    """
    img1_small = cv2.resize(img1, resize_dim)
    img2_small = cv2.resize(img2, resize_dim)
    diff = cv2.absdiff(img1_small, img2_small)
    mean_diff = np.mean(diff)
    return mean_diff < diff_threshold  # 차이가 작으면 True


def is_same_sheet(img1, img2, threshold=0.95, quick_diff_threshold=30):
    """
    빠른 필터 후 SSIM 비교
    """
    if len(img1.shape) == 3:
        img1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    if len(img2.shape) == 3:
        img2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

    # 빠른 필터링
    if not quick_difference(img1, img2, diff_threshold=quick_diff_threshold):
        print(f"빠른 필터링 됨")
        return False

    # SSIM 정밀 비교
    score, _ = ssim(img1, img2, full=True)
    if score >= threshold:
        print(f"정밀 비교 필터링: {score}")
    return score >= threshold


