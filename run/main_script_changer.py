import fitz
from PIL import Image, ImageTk
import tkinter as tk
import os

def convert_pdf_to_image(pdf_path, image_path):
    doc = fitz.open(pdf_path)
    pix = doc[0].get_pixmap()
    pix.save(image_path)
    doc.close()

def on_mouse_down(event):
    global start_y
    start_y = event.y

def on_mouse_up(event):
    end_y = event.y
    crop_pdf_area("input.pdf", "output.pdf", start_y, end_y)
    print(f"Saved cropped PDF from y={start_y} to y={end_y}")
    root.destroy()

def crop_pdf_area(input_pdf, output_pdf, y_start, y_end):
    doc = fitz.open(input_pdf)
    image_files = []

    for page_num in range(len(doc)):
        pix = doc[page_num].get_pixmap()
        image_path = f"page_{page_num}.png"
        pix.save(image_path)
        image_files.append(image_path)

    cropped_images = []
    for image_file in image_files:
        img = Image.open(image_file)
        width, height = img.size
        y1, y2 = sorted((y_start, y_end))
        cropped_img = img.crop((0, y1, width, y2))
        cropped_images.append(cropped_img)

    cropped_images[0].save(output_pdf, save_all=True, append_images=cropped_images[1:])

    for f in image_files:
        os.remove(f)

# 실행 부분
pdf_path = "input.pdf"
image_path = "preview.png"
convert_pdf_to_image(pdf_path, image_path)

root = tk.Tk()
img = Image.open(image_path)
tk_img = ImageTk.PhotoImage(img)

canvas = tk.Canvas(root, width=img.width, height=img.height)
canvas.pack()
canvas.create_image(0, 0, anchor=tk.NW, image=tk_img)

canvas.bind("<ButtonPress-1>", on_mouse_down)
canvas.bind("<ButtonRelease-1>", on_mouse_up)

root.mainloop()
