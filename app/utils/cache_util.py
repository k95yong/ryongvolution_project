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

def add_video_to_cache(url, start_time, end_time, video_path):
    cache = load_video_cache()
    cache.append({
        "url": url,
        "start_time": start_time,
        "end_time": end_time,
        "video_path": video_path
    })
    save_video_cache(cache)


def get_total_cache_size_mb(cache_dir=os.path.join(get_root_dir(), "video_cache")):
    total = 0
    for file in os.listdir(cache_dir):
        path = os.path.join(cache_dir, file)
        if path.endswith(".mp4") and os.path.isfile(path):
            total += os.path.getsize(path)
    return total / (1024 * 1024)  # MB 단위


def cleanup_cache(max_size_mb=1000):
    cache = load_video_cache()
    # mp4 파일의 수정 시간 기준 정렬 (오래된 게 먼저)
    entries_with_mtime = [
        (entry, os.path.getmtime(entry["video_path"]))
        for entry in cache if os.path.exists(entry["video_path"])
    ]
    entries_with_mtime.sort(key=lambda x: x[1])  # 오래된 순
    total_cache_size_mb = get_total_cache_size_mb()
    print(f"🧹 현재 Cached Video 총 용량: {total_cache_size_mb}")
    while total_cache_size_mb > max_size_mb and entries_with_mtime:
        entry, _ = entries_with_mtime.pop(0)
        path = entry["video_path"]
        try:
            os.remove(path)
            print(f"🧹 삭제됨: {path}")
        except Exception as e:
            print(f"❌ 삭제 실패: {e}")
        cache.remove(entry)

    save_video_cache(cache)
