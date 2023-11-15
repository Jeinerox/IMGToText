# -*- coding: utf-8 -*-

from email import message
import tkinter as tk
from tkinter import SEL, filedialog
from tkinter import messagebox
from turtle import update
from PIL import Image, ImageTk
import json
import re
import os
import time


class IMGToText:
    def __init__(self, root):
        self.root = root
        self.root.title("IMGToText")
        self.root.geometry("500x400")
        self.root.resizable(width=False, height=False)

        self.load_saved_data()
        

        # Поле выбора фотографии
        self.photo_path = tk.StringVar()
        self.photo_label = tk.Label(root, text="Select a photo:")
        self.photo_label.pack(pady=5)
        self.photo_entry = tk.Entry(root, textvariable=self.photo_path, width=80)
        self.photo_entry.pack(pady=5)
        self.browse_button = tk.Button(root, text="Open", command=self.browse_photo)
        self.browse_button.pack(pady=5)


        # Текстовое поле для ввода палитры
        self.palette_label = tk.Label(root, text="Palette (from dim to bright)")
        self.palette_label.pack(pady=(20,5))
        self.palette_entry = tk.Entry(root, width=80)
        self.palette_entry.pack(pady=2)
        self.palette_entry.insert(0, self.saved_data.get("palette", ""))

        # Кнопка "По умолчанию" для алфавита
        self.default_button = tk.Button(root, text="Default palette", command=self.default_palette)
        self.default_button.pack(pady=5)
        
        # Чекбокс "Инвертировать цвета"
        self.invert_var = tk.BooleanVar()
        self.invert_var.set(self.saved_data.get("invert", False))
        self.invert_checkbox = tk.Checkbutton(self.root, text="Invert Colors", variable=self.invert_var)
        self.invert_checkbox.pack(pady=5)


        # Текстовое поле для ввода ширины
        self.width_label = tk.Label(root, text="Number of characters horizontally")
        self.width_label.pack(pady=(20,5))
        self.width_entry = tk.Entry(root, width=40)
        self.width_entry.pack(pady=5)
        self.width_entry.insert(0, self.saved_data.get("width", ""))

        # Кнопка начать
        self.start_button = tk.Button(root, text="Launch", command=self.start_processing)
        self.start_button.pack(pady=20)

        # Поле статуса программы 
        self.status_label = tk.Label(self.root, text="Status: Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)

        

    def browse_photo(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.gif")])
        self.photo_path.set(file_path)


    def load_saved_data(self):
        try:
            with open("json/settings.json", "r") as file:
                self.saved_data = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            self.saved_data = {}

    def save_data(self):
        self.saved_data["palette"] = self.palette_entry.get()
        self.saved_data["width"] = self.width_entry.get()
        self.saved_data["invert"] = self.invert_var.get()
        with open("json/settings.json", "w") as file:
            json.dump(self.saved_data, file)

    def default_palette(self):
        self.palette_entry.delete(0, tk.END)
        self.palette_entry.insert(0, '¶@ØÆMåBNÊßÔR#8Q&mÃ0À$GXZA5ñk2S%±3Fz¢yÝCJf1t7ªLc¿+?(r/¤²!*;"^:,\'.`  ')
        self.save_data()

    def update_status(self, new_status):
        self.status_label.config(text=f"Status: {new_status}")
        root.update()
        
    def start_processing(self):
        self.save_data()
        photo_path = self.photo_path.get()
        palette = self.palette_entry.get()
        width_str = self.width_entry.get()
        invert = self.invert_var.get()
        
        # Проверка введенных данных
        if photo_path == "":
            messagebox.showerror("Error", "Photo path is empty");
            return
        # может быть .jpg, .jpeg, .png, .gif
        if not re.match(r".+\.(jpg|jpeg|png|gif)$", photo_path):
            messagebox.showerror("Error", "Invalid file extension");
            return
        try:
            raw_image = Image.open(photo_path)
        except:
            messagebox.showerror("Error", "Invalid file");
            return
        if palette == "":
            messagebox.showerror("Error", "Palette is empty");
            return
        if width_str == "":
            messagebox.showerror("Error", "Width is empty");
            return
        if int(width_str) > 2000:
            messagebox.showerror("Error", "Width is too big, max is 2000");
            return

        # Обработка фотографии

        self.start_button.config(state=tk.DISABLED)
        self.update_status("Processing...")

        target_width = int(width_str)

        symbols = list(palette)
        
        if invert:
            symbols.reverse()

        raw_width, raw_height = raw_image.size
        cropped_image = raw_image.resize((target_width, int(raw_height/(raw_width/target_width)/2)))
        width, height = cropped_image.size
        bw_im = cropped_image.convert('L')
        a = []
        for i in range(width):
            a.append([])
            for j in range(height):
                color = bw_im.getpixel((i, j));
                if color > 200:
                    pass
                a[i].append(symbols[round(color/255*(len(symbols)-1))])

        current_time = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())
        name = 'outputs/'+ os.path.basename(photo_path) + "_" + current_time + ".txt"
        with open(name, 'w', encoding='utf-8') as file:
            for i in range(height):
                for j in range(width):
                    file.write(a[j][i])
                file.write('\n')
                root.update()

        self.save_data()
        self.update_status("Ready")
        self.start_button.config(state=tk.NORMAL)

if __name__ == "__main__":
    root = tk.Tk()
    app = IMGToText(root)
    root.mainloop()
