from guitar_helper import GuitarHelper

title = f"creep radio head"
url = "https://www.youtube.com/watch?v=UayaTO3cypw"
output_root_dir = "C:\\Users\\k95yo\\OneDrive\\바탕 화면\\유투브 다운로드 영상"
# start_time="03:33"
# end_time="04:11"
start_time=None
end_time=None

gh = GuitarHelper(title, url, output_root_dir)
gh.set_bpm(94)
gh.start_time=start_time
gh.end_time=end_time
gh.set_time_range(start_time, end_time)

# gh.download_youtube()
gh.show_capture_guide()
y_start, y_end = map(int, input(f"Y축 시작, 끝 지점을 백분율로 입력하세요 (예: 60 100)\n").split())
gh.capture_video_frame(y_start, y_end)
gh.remove_duplicate_imgs()
gh.apply_bar_numbering_in_dir()
gh.merge_jpgs_to_pdf()

# gh.upload_pdf_to_google_dirve()