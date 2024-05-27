# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk
from tkinter import SEL, filedialog
from tkinter import messagebox
from PIL import Image, ImageTk
import json
import re
import os
import time


class IMGToText:
    def __init__(self, root):
        self.root = root
        self.root.title("IMGToText")
        self.root.geometry("500x500")
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
        
        
        # Выпадающий список палитр
        self.palettes_var = self.saved_data.get("palettes", [])
        self.selected_palette = tk.StringVar(root)
        if self.palettes_var == []:
            self.selected_palette.set('')
        else:
            self.selected_palette.set(self.palettes_var[0])  # Начальное значение        
        self.palette_entry.insert(0, self.selected_palette.get())
        self.palette_menu = ttk.Combobox(root, textvariable=self.selected_palette, values=self.palettes_var, width= 60)
        self.palette_menu.pack(pady=5)
        self.palette_menu.bind("<<ComboboxSelected>>", self.update_palette_entry)
        self.save_button = tk.Button(root, text="Save Palette", command=self.save_palette)
        self.save_button.pack(pady=5)
        self.delete_button = tk.Button(root, text="Delete Palette", command=self.delete_palette)
        self.delete_button.pack()


        
        # Чекбокс "Инвертировать цвета"
        self.invert_var = tk.BooleanVar()
        self.invert_var.set(self.saved_data.get("invert", False))
        self.invert_checkbox = tk.Checkbutton(self.root, text="Invert Colors", variable=self.invert_var)
        self.invert_checkbox.pack(pady=5)

        # Текстовое поле для ввода ширины
        self.width_label = tk.Label(root, text="Number of characters horizontally")
        self.width_label.pack(pady=(20,0))
        self.width_entry = tk.Entry(root, width=10)
        self.width_entry.pack(pady=2)
        self.width_entry.insert(0, self.saved_data.get("width", ""))
        
        # Текстовое поле для ввода пропорций символа
        self.proportions_label = tk.Label(root, text="Symbol proportions (h/w)")
        self.proportions_label.pack(pady=(20,0))
        self.proportions_entry = tk.Entry(root, width=10)
        self.proportions_entry.pack(pady=2)
        self.proportions_entry.insert(0, self.saved_data.get("proportions", ""))        

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
        self.saved_data["palettes"] = self.palettes_var
        self.saved_data["invert"] = self.invert_var.get()
        self.saved_data["width"] = self.width_entry.get()
        self.saved_data["proportions"] = self.proportions_entry.get()
        with open("json/settings.json", "w") as file:
            json.dump(self.saved_data, file)
        
    def save_palette(self):
        if self.palette_entry.get() == '':
            messagebox.showerror("Error", "No palette")
        
        if self.palette_entry.get() in self.palettes_var:
            messagebox.showerror("Error", "Palette already exist")
            return
        self.palettes_var.append(self.palette_entry.get())
        self.save_data()
        self.palette_menu.config(values=self.palettes_var)
        self.selected_palette.set(self.palette_entry.get())
        self.palette_menu.config(textvariable=self.selected_palette)
    
    def delete_palette(self):
        if self.palettes_var == []:
            messagebox.showerror("Error", "Palette list is empty")
            return              
        if self.palette_entry.get() not in self.palettes_var:
            messagebox.showerror("Error", "Palette didnt found")
            return            
        self.palettes_var.remove(self.palette_entry.get())
        self.save_data()
        self.palette_menu.config(values=self.palettes_var)
        if self.palettes_var != []:
            self.selected_palette.set(self.palettes_var[0])
        else:
            self.selected_palette.set('')   
        self.palette_menu.config(textvariable=self.selected_palette)    
        self.update_palette_entry(0)
            
    def update_palette_entry(self, event):
        selected_palette = self.selected_palette.get()
        self.palette_entry.delete(0, tk.END)
        self.palette_entry.insert(0, selected_palette)

    def update_status(self, new_status):
        self.status_label.config(text=f"Status: {new_status}")
        root.update()
        
    def start_processing(self):
        #self.save_data()
        photo_path = self.photo_path.get()
        palette = self.palette_entry.get()
        width_str = self.width_entry.get()
        invert = self.invert_var.get()
        proportions_str = self.proportions_entry.get()
        
        # Проверка введенных данных
        if photo_path == "":
            messagebox.showerror("Error", "Photo path is empty");
            return
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
        try:
            int(width_str)
        except:
            messagebox.showerror("Error", "Width should be number");
            return
        try:
            float(proportions_str)
        except:
            messagebox.showerror("Error", "Proportions should be number");
            return        
        if float(proportions_str) <=0 or float(proportions_str)>10:
            messagebox.showerror("Error", "Proportions should be >=0 and <=10");
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
        
        proportions = float(proportions_str)
        raw_width, raw_height = raw_image.size
        cropped_image = raw_image.resize((target_width, int(raw_height/(raw_width/target_width)/proportions)))
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
