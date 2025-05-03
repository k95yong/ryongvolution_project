import shutil
import subprocess
import tempfile

import numpy as np
import yt_dlp
from skimage.metrics import structural_similarity as ssim
from datetime import datetime
from moviepy.editor import VideoFileClip

from utils.cache_util import load_video_cache, add_video_to_cache, cleanup_cache


def download_youtube(url, output_path='downloaded_video.mp4', start_time=None, end_time=None):
    start_time = convert_to_hms(start_time)
    end_time = convert_to_hms(end_time)

    cached_path = find_cached_video(url, start_time, end_time)
    if cached_path:
        print(f"✅ 캐시된 영상 있음: {cached_path} → 다운로드 생략")
        return cached_path

    temp_path = 'temp_downloaded_video.mp4'
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',  # 영상 + 오디오
        'merge_output_format': 'mp4',  # mp4로 병합 저장
        'outtmpl': temp_path,  # 저장 경로
        'quiet': False  # 로그 출력
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

    # ✅ 다운로드 후 캐시에 추가
    add_video_to_cache(url, start_time, end_time, output_path)
    cleanup_cache(max_size_mb=5000)
    print(f"📝 캐시에 추가됨: {output_path}")
    return output_path

def convert_to_hms(timestr):
    """MM:SS 형식을 HH:MM:SS로 바꿔주는 함수"""
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
        for i in range(10, 100, 10):
            y = int(height * (i / 100))
            cv2.line(frame, (0, y), (width, y), (0, 255, 0), 1)
            cv2.putText(frame, f"{i}%", (10, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

        cv2.imshow('Guide Frame', frame)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    else:
        print("가이드 프레임 읽기 실패")

    cap.release()
    return


import cv2


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
        return guide_img_path
    else:
        print("가이드 프레임 읽기 실패")
        return None

    cap.release()


def capture_video_frame(video_path, output_dir, interval_sec=5, y_start=60, y_end=100):
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=True)
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print("비디오 열기 실패")
        return

    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_interval = int(fps * interval_sec)

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    crop_start_y = int(height * (y_start / 100))
    crop_end_y = int(height * (y_end / 100))
    if crop_start_y > crop_end_y:
        print("캡처 영역을 올바르게 지정하세요.")
        return

    frame_idx = 0

    while frame_idx < total_frames:
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        ret, frame = cap.read()

        if not ret:
            break

        crop_image = frame[crop_start_y:crop_end_y, :]
        gray_image = cv2.cvtColor(crop_image, cv2.COLOR_BGR2GRAY)

        current_time_sec = frame_idx / fps
        timestamp = seconds_to_timestamp(current_time_sec)

        temp_dir = tempfile.gettempdir()
        temp_save_path = os.path.join(temp_dir, f"temp_{timestamp}.jpg")

        cv2.imwrite(temp_save_path, gray_image)
        success = cv2.imwrite(temp_save_path, gray_image)
        if success:
            print(f"Saved {temp_save_path}")
            final_save_path = os.path.join(output_dir, f"frame_{timestamp}.jpg")
            shutil.move(temp_save_path, final_save_path)
        else:
            print(f"Failed to save {temp_save_path}")

        print(f"bottom_crop size: {gray_image.shape}")
        frame_idx += frame_interval

    cap.release()


def seconds_to_timestamp(sec):
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = int(sec % 60)
    return f"{h:02d}_{m:02d}_{s:02d}"


from PIL import Image
import os


def merge_jpgs_vertically_to_pdf(image_dir, output_pdf_path, pdf_title):
    # 디렉토리 안에 있는 jpg 파일들 정렬해서 가져오기
    images = [os.path.join(image_dir, f) for f in sorted(os.listdir(image_dir)) if f.lower().endswith('.jpg')]
    if not images:
        print("jpg 파일이 없습니다.")
        return None

    # 이미지들 로드
    loaded_images = [Image.open(img_path).convert('RGB') for img_path in images]

    # 각 이미지 크기 가져오기
    widths, heights = zip(*(img.size for img in loaded_images))

    # 가로 길이는 최대, 세로 길이는 합계
    max_width = max(widths)
    total_height = sum(heights)

    # 새 캔버스 생성
    merged_image = Image.new('RGB', (max_width, total_height), color=(255, 255, 255))

    # 이미지 하나씩 붙이기
    y_offset = 0
    for img in loaded_images:
        merged_image.paste(img, (0, y_offset))
        y_offset += img.size[1]

    os.makedirs(output_pdf_path, exist_ok=True)
    pdf_file_path = os.path.join(output_pdf_path, f"{pdf_title}.pdf")
    # PDF로 저장
    merged_image.save(pdf_file_path, "PDF", resolution=100.0)
    # set_pdf_title(output_pdf_path, pdf_title)

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
                print(f"중복 이미지로 판단됨 → 이동: {img_path}")
                shutil.move(img_path, os.path.join(dup_dir, os.path.basename(img_path)))
            prev_img = img


def is_same_sheet(img1, img2, threshold=0.95):
    if len(img1.shape) == 3:
        img1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    if len(img2.shape) == 3:
        img2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

    # SSIM 계산
    score, _ = ssim(img1, img2, full=True)
    if 0.8 < score < threshold:
        print(f"중복 의심: {score}")
    return score >= threshold
