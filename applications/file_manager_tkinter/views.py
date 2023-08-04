# -*- coding: utf-8 -*-
"""
Created on Thu Jul  6 11:15:58 2023

@author: drug1
"""

import tkinter as tk
import os
import sys
import psutil
import pyautogui
import time
from tkinter import ttk, Scrollbar, Canvas
import asyncio
from PIL import Image, ImageTk
import tkinter
import os
import subprocess
from tkinter import messagebox
from tkinter import simpledialog
from tkinter import filedialog

from file_actions import DefoltContextMenu, FolderContextMenu, FileContextMenu
import file_actions

file_manager2 = None
file_manager3 = None

class FileManager():
    ''' Родительский Класс основного окна'''

    def __init__(self, frame):
        self.file_context_menu = None
        self.defolt_context_menu = None
        self.folder_context_menu = None
        self.item_path = None

        self.frame = frame
        self.canvas = tkinter.Canvas(self.frame, borderwidth=0, bg="lightgray")

        self.drive_letter = self.get_drives()[0][0]
        self.current_path = self.get_drives()[0]
        self.parent_dir = self.get_drives()[0]
        self.icon_set()
        self.label_text = self.current_path
        self.path_label = tk.Label(self.frame, text=self.label_text)
        self.path_label.pack()
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.treeview = self.create_tree(self.canvas)
        self.treeview.pack(fill=tk.BOTH, expand=True)
        self.context_menu1()
        self.treeview.bind('<<TreeviewSelect>>', self.on_treeview_select)
        self.treeview.bind('<Double-Button-1>', self.on_double_click)

    # Обработчик события выделения элемента
    def on_treeview_select(self, event):
        # Получаем список выделенных элементов
        self.selected_items = self.treeview.selection()

    # Метод для получения списка выбранных элементов
    def get_selected_items(self):
        return self.selected_items

    def context_menu1(self):
        self.treeview.bind("<Button-3>", self.show_context_menu)
        self.canvas.bind("<Button-3>", self.show_context_menu)

    # функция вызова Контекстного меню
    def show_context_menu(self, event):
        try:
            item = self.treeview.identify("item", event.x, event.y)
        except:
            item = None
        if item:
            selected_items = self.get_selected_items()
            # Выделяем элемент перед вызовом контекстного меню
            self.treeview.selection_set(item)
            # Если выбран файл или папка, вызовите контекстное меню для элемента
            item_path = self.treeview.item(item, "text")
            item_path = os.path.join(self.current_path, item_path)

            self.item_path = item_path

            if os.path.isdir(item_path):

                # Если выбрана папка, вызовите контекстное меню для папки
                self.folder_context_menu = FolderContextMenu(self, self.treeview, self.item_path)
                x, y, _, _ = self.treeview.bbox(item)
                self.folder_context_menu.coordinate_set(x + 36, y + 10)
                self.folder_context_menu.post(event.x_root, event.y_root)
            else:
                # Получаем значение из столбца "Тип" для выбранного элемента
                item_type = self.treeview.set(item, "Type")
                self.item_path = self.item_path + item_type
                self.file_context_menu = FileContextMenu(self, self.treeview, self.item_path)
                x, y, _, _ = self.treeview.bbox(item)
                self.file_context_menu.coordinate_set(x + 36, y + 10)
                self.file_context_menu.post(event.x_root, event.y_root)
        else:

            # Если кликнули по пустому пространству окна, вызовите контекстное меню для окна
            self.defolt_context_menu = DefoltContextMenu(self, self.canvas, self.current_path)

            self.defolt_context_menu.post(event.x_root, event.y_root)

        #self.menu_defolt.post(event.x_root, event.y_root)
        #self.update_file_system()

    '''Очистка дерева перед обновлением'''

    def clear_tree(self, tree):
        tree.delete(*tree.get_children())

    '''ПОЛУЧЕНИЕ ИКОНОК'''

    def icon_set(self):
        path_folder, path_file, path_left = self.path_icon()
        self.folder_icon = self.load_icon(path_folder)
        self.default_file_icon = self.load_icon(path_file)
        self.left_icon = self.load_icon(path_left)
        self.file_icons = {
            ".txt": self.load_icon(path_file),
            ".png": self.load_icon(path_file),
            ".pdf": self.load_icon(path_file),
            # Добавьте другие иконки файлов по мере необходимости
        }

    '''пути до иконок'''

    def path_icon(self):
        current_directory = os.path.dirname(os.path.abspath(sys.argv[0]))
        path_folder = os.path.join(current_directory, "icons", "2.png")
        path_file = os.path.join(current_directory, "icons", "1.png")
        path_left = os.path.join(current_directory, "icons", "3.png")
        return path_folder, path_file, path_left

    '''# функция загрузки иконки'''

    def load_icon(self, icon_filename):
        icon_path = os.path.join(os.getcwd(), icon_filename)
        icon_image = Image.open(icon_path).resize((16, 16), Image.LANCZOS)
        icon = ImageTk.PhotoImage(icon_image)
        return icon

    def create_tree(self, canvas):
        # Создание дерева
        self.treeview = ttk.Treeview(canvas, columns=("Type", "Size"))
        self.treeview.heading("#0", text="Имя файла/папки", anchor='w')
        self.treeview.heading("Size", text="Размер")
        self.treeview.heading("Type", text="Тип")
        self.treeview.column("#0", width=200)
        self.treeview.column("Type", width=50)
        self.treeview.column("Size", width=70, anchor='center')
        self.treeview.column("Size", anchor='center', stretch=False)
        self.treeview.column("Type", anchor='center', stretch=False)
        treeview_style = ttk.Style()
        treeview_style.configure("Treeview", background="lightgray")
        return self.treeview

    def get_drives(self):
        drives = []
        for drive in psutil.disk_partitions():
            if drive.mountpoint:
                drives.append(drive.device)
        return drives

    def get_files_and_folders(self, path):
        files_and_folders = os.listdir(path)
        files = [f for f in files_and_folders if os.path.isfile(os.path.join(path, f))]
        folders = [f for f in files_and_folders if os.path.isdir(os.path.join(path, f))]
        return files, folders

    '''первоначальная загрузка файловой системы'''

    def load_file_system(self):
        try:
            files, folders = self.get_files_and_folders(self.current_path)
            for folder in folders:
                self.treeview.insert('', 'end', text=folder, image=self.folder_icon, values=("Папка", ""))
            for file in files:
                file_name = os.path.basename(file)
                file_extension = os.path.splitext(file_name)[1]
                file_name1 = os.path.splitext(file_name)[0]
                file_name_ful = os.path.join(self.current_path, file_name)
                file_size = self.get_size(file_name_ful)
                if file_extension in self.file_icons:
                    icon = self.file_icons[file_extension]
                else:
                    icon = self.default_file_icon
                self.treeview.insert('', 'end', text=file_name1, image=icon, values=(file_extension, file_size))
        except PermissionError:
            self.treeview.insert('', 'end', text="  СКРЫТАЯ ПАПКА", image=self.left_icon, values=("Папка",))
            # Обработка ошибки доступа к директории
            # Например, можно вывести сообщение об ошибке или предпринять другие действия

    # разделение списка файлов и папок в текущей директории
    def update_file_system(self):

        if os.path.isdir(self.current_path):
            try:
                self.treeview.delete(*self.treeview.get_children())
                files, folders = self.get_files_and_folders(self.current_path)
                parent_path = os.path.abspath(os.path.join(self.current_path, os.pardir))
                if not os.path.ismount(self.current_path):
                    self.treeview.insert('', 'end', text="..", image=self.left_icon, values=("Папка", parent_path))
                for folder in folders:
                    folder_name = os.path.basename(folder)
                    self.treeview.insert('', 'end', text=folder_name, image=self.folder_icon, values=("Папка", ""))
                for file in files:
                    file_name = os.path.basename(file)
                    file_extension = os.path.splitext(file_name)[1]
                    file_name1 = os.path.splitext(file_name)[0]
                    file_name_ful = os.path.join(self.current_path, file_name)
                    file_size = self.get_size(file_name_ful)
                    if file_extension in self.file_icons:
                        icon = self.file_icons[file_extension]
                    else:
                        icon = self.default_file_icon
                    self.treeview.insert('', 'end', text=file_name1, image=icon, values=(file_extension, file_size))
            except PermissionError:
                self.treeview.insert('', 'end', text="  СКРЫТАЯ ПАПКА", image=self.left_icon, values=("Папка",))



    # Метод для получения размера файла в удобочитаемом формате
    def get_size(self, file_path):
        size = os.path.getsize(file_path)
        for unit in ['Б', 'КБ', 'МБ', 'ГБ']:
            if size < 1024.0:
                return "%3.1f %s" % (size, unit)
            size /= 1024.0
        return "%3.1f %s" % (size, unit)


    def on_double_click(self, event):
        selected_items = self.treeview.selection()
        if selected_items:
            selected_item = selected_items[0]

            item_text = self.treeview.item(selected_item, "text")

            if item_text == "  СКРЫТАЯ ПАПКА":
                parent_dir = os.path.abspath(os.path.join(self.current_path, os.pardir))
                self.current_path = parent_dir
                self.path_label.config(text=self.current_path)
            if item_text == "..":  # Проверяем, выбран ли элемент с двумя точками
                # Переходим на уровень выше

                self.parent_dir = os.path.abspath(os.path.join(self.current_path, os.pardir))
                if os.path.exists(self.parent_dir):  # Проверяем, существует ли родительский каталог
                    self.current_path = self.parent_dir
                    self.path_label.config(text=self.current_path)
            else:
                # Получаем полный путь элемента, добавляя его к текущему пути
                item_path = os.path.join(self.current_path, item_text)

                # Если выбрана папка, переходим в неё и обновляем содержимое
                if os.path.isdir(item_path) and not os.path.islink(item_path):
                    self.current_path = item_path

                    # Обновляем метку с текущим путем
                    self.path_label.config(text=self.current_path + "\\")
            # Обновляем содержимое списка файлов и папок
            self.update_file_system()


class FileManagerList_2(FileManager):
    ''' Класс основного окна, наследующий FileManager'''

    def __init__(self, frame):
        super().__init__(frame)

        self.load_drive_options()
        self.load_file_system()

    def load_drive_options(self):
        drive_list = self.get_drives()
        for drive in drive_list:
            drive_option = tk.Button(self.frame, text=drive, command=lambda d=drive: self.change_drive(d))
            drive_option.pack(side=tk.LEFT)

    '''функция нажатия кнопки смены привода'''

    def change_drive(self, drive):
        self.drive_letter = drive[0]
        self.current_path = drive
        self.path_label.config(text=self.current_path)
        self.update_file_system()


class FileManagerList(FileManager):
    ''' Класс основного окна, наследующий FileManager'''

    def __init__(self, frame):
        super().__init__(frame)



        self.load_drive_options()
        self.load_file_system()

    ''' загрузка кнопок приводов'''

    def load_drive_options(self):
        drive_list = self.get_drives()
        for drive in drive_list:
            drive_option = tk.Button(self.frame, text=drive, command=lambda d=drive: self.change_drive(d))
            drive_option.pack(side=tk.LEFT)

    '''функция нажатия кнопки смены привода'''

    def change_drive(self, drive):
        self.drive_letter = drive[0]
        self.current_path = drive
        self.path_label.config(text=self.current_path)
        self.update_file_system()

def update_ful():
    global file_manager2
    global file_manager3
    file_manager2.update_file_system()
    file_manager3.update_file_system()

def applications(root):
    # initial_path = psutil.disk_partitions()[0][0]

    # frame1 = tk.Frame(root, bg="#A9A9A9")
    # frame1.pack(side=tk.LEFT, padx=4, pady=4, fill=tk.BOTH, expand=False)
    global file_manager2
    global file_manager3

    frame2 = tk.Frame(root, bg="lightgray")
    frame2.pack(side=tk.LEFT, padx=4, pady=4, fill=tk.BOTH, expand=True)

    frame3 = tk.Frame(root, bg="#A9A9A9")
    frame3.pack(side=tk.LEFT, padx=4, pady=4, fill=tk.BOTH, expand=True)

    file_manager2 = FileManagerList_2(frame2)
    file_manager3 = FileManagerList(frame3)

