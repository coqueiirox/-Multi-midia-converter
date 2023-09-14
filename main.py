import math
import struct
import numpy as np
import wave
import scipy.ndimage
from PIL import Image, ImageEnhance
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

ASCII_CHARS = [' ', '.', '*', ':', 'o', '&', '8', '#', '@']

def load_image(img_path):
    return Image.open(img_path).convert('L')

def enhance_image(img):
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(2.0)
    return img

def image_to_ascii(img, scale=10):
    img = enhance_image(img)
    new_width = int(img.width / scale)
    new_height = int(img.height / scale)
    ascii_img = ''
    for y in range(new_height):
        for x in range(new_width):
            pixel_value = img.getpixel((x * scale, y * scale))
            char_index = int(pixel_value / 255 * (len(ASCII_CHARS) - 1))
            ascii_img += ASCII_CHARS[char_index]
        ascii_img += '\n'
    return ascii_img

def save_to_file(content, file_path):
    with open(file_path, 'w') as f:
        f.write(content)

def generate_audio_from_image(img_path, output, duration=5.0, sampleRate=44100.0):
    max_frame = int(duration * sampleRate)
    imgMat = scipy.ndimage.zoom(np.array(load_image(img_path)),
                                (400 / np.array(load_image(img_path)).shape[0],
                                max_frame / np.array(load_image(img_path)).shape[1]),
                                order=0)
    with wave.open(output, 'w') as wavef:
        wavef.setnchannels(1)
        wavef.setsampwidth(2)
        wavef.setframerate(sampleRate)
        for frame in range(max_frame):
            signalValue = 0
            count = 0
            for step in range(int(22000 / 400)):
                intensity = imgMat[step, frame] * 32767
                if intensity < 0.1 * 32767:
                    continue
                for freq in range(step * 400, (step + 1) * 400, 1000):
                    signalValue += intensity * math.cos(freq * 2 * math.pi * frame / sampleRate)
                    count += 1
            if count:
                signalValue /= count
            signalValue = max(-32768, min(32767, signalValue))
            data = struct.pack('<h', int(signalValue))
            wavef.writeframes(data)


def main_gui():
    def convert_image():
        image_path = image_path_entry.get()
        output_dir = output_dir_entry.get()
        scale = int(scale_entry.get())
        result = image_to_ascii(load_image(image_path), scale)
        save_to_file(result, f"{output_dir}/output_ascii.txt")
        messagebox.showinfo("Conversion Complete", "Image to ASCII conversion completed.")

    def convert_audio():
        audio_image_path = audio_image_path_entry.get()
        audio_output_dir = audio_output_dir_entry.get()
        duration = float(duration_entry.get())
        generate_audio_from_image(audio_image_path, f"{audio_output_dir}/output_audio.wav", duration)
        messagebox.showinfo("Conversion Complete", "Image to Audio conversion completed.")

    def browse_image():
        file_path = filedialog.askopenfilename()
        image_path_entry.delete(0, tk.END)
        image_path_entry.insert(0, file_path)

    def browse_audio_image():
        file_path = filedialog.askopenfilename()
        audio_image_path_entry.delete(0, tk.END)
        audio_image_path_entry.insert(0, file_path)

    def browse_output_dir():
        output_dir = filedialog.askdirectory()
        output_dir_entry.delete(0, tk.END)
        output_dir_entry.insert(0, output_dir)

    def browse_audio_output_dir():
        output_dir = filedialog.askdirectory()
        audio_output_dir_entry.delete(0, tk.END)
        audio_output_dir_entry.insert(0, output_dir)

    root = tk.Tk()
    root.title("Multimedia Converter")
    root.geometry("500x300")
    root.configure(bg='black')

    notebook = ttk.Notebook(root)

    tab1 = ttk.Frame(notebook)
    tab2 = ttk.Frame(notebook)

    notebook.add(tab1, text="Image to ASCII")
    notebook.add(tab2, text="Image to Audio")

    image_path_label = ttk.Label(tab1, text="Image Path:")
    image_path_label.pack()
    image_path_entry = ttk.Entry(tab1)
    image_path_entry.pack()

    browse_button = ttk.Button(tab1, text="Browse", command=browse_image)
    browse_button.pack()

    output_dir_label = ttk.Label(tab1, text="Output Directory:")
    output_dir_label.pack()
    output_dir_entry = ttk.Entry(tab1)
    output_dir_entry.pack()

    browse_output_button = ttk.Button(tab1, text="Browse", command=browse_output_dir)
    browse_output_button.pack()

    scale_label = ttk.Label(tab1, text="Scale Factor (default 10):")
    scale_label.pack()
    scale_entry = ttk.Entry(tab1)
    scale_entry.insert(tk.END, "10")
    scale_entry.pack()

    convert_button = ttk.Button(tab1, text="Convert", command=convert_image)
    convert_button.pack()

    audio_image_path_label = ttk.Label(tab2, text="Image Path:")
    audio_image_path_label.pack()
    audio_image_path_entry = ttk.Entry(tab2)
    audio_image_path_entry.pack()

    browse_audio_button = ttk.Button(tab2, text="Browse", command=browse_audio_image)
    browse_audio_button.pack()

    audio_output_dir_label = ttk.Label(tab2, text="Output Directory:")
    audio_output_dir_label.pack()
    audio_output_dir_entry = ttk.Entry(tab2)
    audio_output_dir_entry.pack()

    browse_audio_output_button = ttk.Button(tab2, text="Browse", command=browse_audio_output_dir)
    browse_audio_output_button.pack()

    duration_label = ttk.Label(tab2, text="Duration (default 5.0 seconds):")
    duration_label.pack()
    duration_entry = ttk.Entry(tab2)
    duration_entry.insert(tk.END, "5.0")
    duration_entry.pack()

    convert_audio_button = ttk.Button(tab2, text="Convert", command=convert_audio)
    convert_audio_button.pack()

    notebook.pack(fill=tk.BOTH, expand=True)
    root.mainloop()

if __name__ == "__main__":
    main_gui()
