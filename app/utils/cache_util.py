import os
import json

from app.utils.path_util import get_root_dir

CACHE_PATH = os.path.join(get_root_dir(), "video_cache", "cache.json")


def load_video_cache():
    if not os.path.exists(CACHE_PATH):
        return []

    with open(CACHE_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)  # ✅ 파일 핸들 f를 넣어줘야 함
        return data.get("videos", [])


def save_video_cache(entries):
    with open(CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump({"videos": entries}, f, indent=2, ensure_ascii=False)


def get_total_cache_size_mb(cache_dir=os.path.join(get_root_dir(), "video_cache")):
    total = 0
    for file in os.listdir(cache_dir):
        path = os.path.join(cache_dir, file)
        if path.endswith(".mp4") and os.path.isfile(path):
            total += os.path.getsize(path)
    return total / (1024 * 1024)


def cleanup_files(resource_name: str):
    video_resource_path = os.path.join(get_root_dir(), 'temp', f"{resource_name}.mp4")
    guide_img_path = os.path.join(get_root_dir(), 'static', 'img', f"{resource_name}.jpg")
    if os.path.exists(video_resource_path):
        os.remove(video_resource_path)
    if os.path.exists(guide_img_path):
        os.remove(guide_img_path)
    print(f"🧹 임시 파일 (Video, Guide img) 정리 완료")
