import tkinter as tk
from tkinter import ttk, messagebox
from guitar_helper import GuitarHelper

def run_selected_functions():
    output_dir = str(output_dir_entry.get())
    title = str(title_entry.get())
    url = str(url_entry.get())
    start_time = str(start_time_entry.get())
    end_time = str(end_time_entry.get())
    if str(bottom_property_entry.get()).startswith('ex)'):
        bottom_property = 40
    else:
        bottom_property = int(bottom_property_entry.get())
    if str(bpm_entry.get()).startswith('ex)'):
        bpm = None
    else:
        bpm = int(bpm_entry.get())
    note = str(note_entry.get())

    if not (output_dir and title and url and start_time and bpm and note):
        messagebox.showerror("오류", "필수 필드를 입력해 주세요.")
        return

    # 'ex)'로 시작하거나 빈 경우 None 처리
    if end_time == '' or end_time.strip().lower().startswith('ex)') or end_time.strip().startswith('('):
        end_time = None

    gh = GuitarHelper(title, url, output_dir)
    gh.set_time_range(start_time=start_time, end_time=end_time)
    gh.set_bpm_note_info(bpm, note)

    try:
        if download_var.get():
            gh.download_youtube()
        if capture_var.get():
            gh.capture_video_frame(bottom_percent=bottom_property)
        if merge_var.get():
            gh.merge_jpgs_to_pdf()
        if upload_var.get():
            gh.upload_pdf_to_google_dirve()

        messagebox.showinfo("성공", "선택한 함수들 실행 완료!")
    except Exception as e:
        messagebox.showerror("실패", str(e))

def add_placeholder(entry, placeholder_text):
    entry.insert(0, placeholder_text)
    entry.config(fg='gray')
    def on_focus_in(event):
        if entry.get() == placeholder_text:
            entry.delete(0, tk.END)
            entry.config(fg='black')
    def on_focus_out(event):
        if entry.get() == '':
            entry.insert(0, placeholder_text)
            entry.config(fg='gray')
    entry.bind("<FocusIn>", on_focus_in)
    entry.bind("<FocusOut>", on_focus_out)

# Tkinter 기본 세팅
root = tk.Tk()
root.title("Guitar Helper 실행기")

# 안내 문구
tk.Label(root, text="* 표시된 항목은 필수 입력입니다.", fg="red").grid(row=0, column=0, columnspan=2, pady=(5, 10))

# 입력창
label_width = 18
entry_width = 40

tk.Label(root, text="* Output Directory", width=label_width, anchor="e").grid(row=1, column=0)
output_dir_entry = tk.Entry(root, width=entry_width)
output_dir_entry.grid(row=1, column=1)
add_placeholder(output_dir_entry, "ex) C:\\Users\\User\\Path")

tk.Label(root, text="* Title", width=label_width, anchor="e").grid(row=2, column=0)
title_entry = tk.Entry(root, width=entry_width)
title_entry.grid(row=2, column=1)
add_placeholder(title_entry, "ex) don't look back pt_2")

tk.Label(root, text="URL", width=label_width, anchor="e").grid(row=3, column=0)
url_entry = tk.Entry(root, width=entry_width)
url_entry.grid(row=3, column=1)
add_placeholder(url_entry, "ex) https://www.youtube.com/watch?v=xxxx")

tk.Label(root, text="Start Time (00:00:00)", width=label_width, anchor="e").grid(row=4, column=0)
start_time_entry = tk.Entry(root, width=entry_width)
start_time_entry.grid(row=4, column=1)
add_placeholder(start_time_entry, "ex) 00:05:22")

tk.Label(root, text="End Time (선택)", width=label_width, anchor="e").grid(row=5, column=0)
end_time_entry = tk.Entry(root, width=entry_width)
end_time_entry.grid(row=5, column=1)
add_placeholder(end_time_entry, "(비워두면 전체)")

tk.Label(root, text="Bottom Property(%)", width=label_width, anchor="e").grid(row=6, column=0)
bottom_property_entry = tk.Entry(root, width=entry_width)
bottom_property_entry.grid(row=6, column=1)
add_placeholder(bottom_property_entry, "ex) 40")

tk.Label(root, text="BPM", width=label_width, anchor="e").grid(row=7, column=0)
bpm_entry = tk.Entry(root, width=entry_width)
bpm_entry.grid(row=7, column=1)
add_placeholder(bpm_entry, "ex) 82")

tk.Label(root, text="Note (ex: 4/4)", width=label_width, anchor="e").grid(row=8, column=0)
note_entry = tk.Entry(root, width=entry_width)
note_entry.grid(row=8, column=1)
add_placeholder(note_entry, "ex) 4/4")

# 함수 선택 체크박스
frame = tk.Frame(root)
frame.grid(row=9, column=0, columnspan=2, pady=10)

download_var = tk.BooleanVar()
capture_var = tk.BooleanVar()
merge_var = tk.BooleanVar()
upload_var = tk.BooleanVar()

chk1 = tk.Checkbutton(frame, text="Download YouTube", variable=download_var)
chk1.pack(anchor='w')
chk2 = tk.Checkbutton(frame, text="Capture Bottom Frames", variable=capture_var)
chk2.pack(anchor='w')
chk3 = tk.Checkbutton(frame, text="Merge JPGs to PDF", variable=merge_var)
chk3.pack(anchor='w')
chk4 = tk.Checkbutton(frame, text="Upload PDF to Google Drive", variable=upload_var)
chk4.pack(anchor='w')

# 실행 버튼
run_button = tk.Button(root, text="실행", command=run_selected_functions)
run_button.grid(row=10, column=0, columnspan=2, pady=10)

root.mainloop()