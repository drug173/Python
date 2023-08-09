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

from file_actions import ContextMenu
import file_actions

file_manager2 = None
file_manager3 = None


class FileManager():
    ''' Родительский Класс основного окна'''

    def __init__(self, frame):

        self.file_context_menu = None
        self.defolt_context_menu = None
        self.folder_context_menu = None

        self.context_menu = None
        self.selected_items = None

        self.item_path = None
        # Переменные для отслеживания выделения
        self.selecting = False
        self.start_item = None
        self.end_item = None
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
        self.selected_file_folders_names = []
        self.binding()

    '''События мыши'''

    # Привязываем обработчики к событиям мыши
    def binding(self):
        self.context_menu1()
        self.treeview.bind("<Button-1>", self.on_treeview_click)
        self.treeview.bind("<B1-Motion>", self.on_treeview_drag)
        self.treeview.bind("<ButtonRelease-1>", self.on_treeview_release)
        # self.treeview.bind('<<TreeviewSelect>>', self.on_treeview_select)
        self.treeview.bind('<Double-Button-1>', self.on_double_click)

    # Вызов контекстного меню
    def context_menu1(self):
        self.treeview.bind("<Button-3>", self.show_context_menu)
        self.canvas.bind("<Button-3>", self.show_context_menu)

    '''Выделение элементов'''

    # Обработчик начала выделения
    def on_treeview_click(self, event):
        self.selecting = True
        self.start_item = self.treeview.identify_row(event.y)
        self.end_item = self.start_item
        self.update_selection()

    # Обработчик перемещения мыши при выделении
    def on_treeview_drag(self, event):
        if self.selecting:
            self.end_item = self.treeview.identify_row(event.y)
            self.update_selection()

    # Обработчик завершения выделения
    def on_treeview_release(self, event):
        self.selecting = False
        self.start_item = None
        self.end_item = None
        selected_items = self.treeview.selection()
        self.selected_file_folders_names = []
        for item in selected_items:
            file_name = self.treeview.item(item, "text")
            type1 = self.treeview.set(item, "Type")
            if type1 != "Папка":
                print(type1)
                file_name = file_name + type1
            self.selected_file_folders_names.append(file_name)

        if self.selected_file_folders_names:
            print("Selected file names2", self.selected_file_folders_names)

    # Обновление состояния выделения
    def update_selection(self):
        self.treeview.selection_clear()
        if self.start_item and self.end_item:
            items = self.treeview.get_children()
            start_index = items.index(self.start_item)
            end_index = items.index(self.end_item)
            for index in range(min(start_index, end_index), max(start_index, end_index) + 1):
                self.treeview.selection_add(items[index])

    # Обработчик события выделения элемента
    def on_treeview_select(self, event):
        # Получаем список выделенных элементов
        self.selected_items = self.treeview.selection()
        print("контекст", self.selected_items)

    '''КОНТЕКСТНОЕ МЕНЮ'''

    # функция вызова Контекстного меню
    def show_context_menu(self, event):
        try:  # получаем координаты клика правой кнопкой
            item = self.treeview.identify("item", event.x, event.y)
            print(item)
            print("клик по..")
        except:
            print("клик мимо.")
            item = None
        self.on_treeview_select(event)
        if item:  # Если клик правой кнопкой по элементу
            self.on_treeview_select(event)
            action_field = self.treeview
            print("1", self.selected_items)
            if item not in self.selected_items:  # Если клик правой кнопкой не по выделенному элементу
                self.treeview.selection_set(item)  # Выделяем элемент по которому был клик правой кнопкой
                print("2", item)
                self.selected_items = (item,)
                print("3", self.selected_items)
        else:
            self.selected_items = ()
            action_field = self.canvas
        self.context_menu = ContextMenu(self, action_field, self.current_path, self.selected_items)
        if action_field == self.treeview:
            x, y, _, _ = self.treeview.bbox(item)
            self.context_menu.coordinate_set(x + 36, y + 10)
        print("action_field", action_field)
        print("type", type(action_field))
        # self - передаём в функцию фрейм
        # action_field - по чему был клик (дерево или окно: treeview или canvas)
        # self.current_path - текущая папка
        # self.selected_items - кортеж выбранных файлов и папок
        print("self.current_path", self.current_path)
        self.context_menu.post(event.x_root, event.y_root)

    '''Очистка дерева перед обновлением'''

    def clear_tree(self, tree):
        tree.delete(*tree.get_children())

    '''ПОЛУЧЕНИЕ ИКОНОК'''

    # ИКОНКИ ДЛЯ ПАПОК И ФАЙЛОВ
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

    # ПУТИ ДО ИКОНОК
    def path_icon(self):
        current_directory = os.path.dirname(os.path.abspath(sys.argv[0]))
        path_folder = os.path.join(current_directory, "icons", "2.png")
        path_file = os.path.join(current_directory, "icons", "1.png")
        path_left = os.path.join(current_directory, "icons", "3.png")
        return path_folder, path_file, path_left

    # функция загрузки иконки
    def load_icon(self, icon_filename):
        icon_path = os.path.join(os.getcwd(), icon_filename)
        icon_image = Image.open(icon_path).resize((16, 16), Image.LANCZOS)
        icon = ImageTk.PhotoImage(icon_image)
        return icon

    '''СОЗДАНИЕ ДЕРЕВА'''
    # Дерево
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

    '''Получение списка приводов'''

    def get_drives(self):
        drives = []
        for drive in psutil.disk_partitions():
            if drive.mountpoint:
                drives.append(drive.device)
        return drives

    '''ЗАГРУЗКА ФАЙЛОВОЙ СИСТЕМЫ'''

    # Разделение списка элементов текущей директории на два списка файлов и папок
    def get_files_and_folders(self, path):
        files_and_folders = os.listdir(path)
        files = [f for f in files_and_folders if os.path.isfile(os.path.join(path, f))]
        folders = [f for f in files_and_folders if os.path.isdir(os.path.join(path, f))]
        return files, folders

    # первоначальная загрузка файловой системы
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

    # Обновление файловой системы
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

    '''Метод для получения размера файла в удобочитаемом формате'''
    def get_size(self, file_path):
        size = os.path.getsize(file_path)
        for unit in ['Б', 'КБ', 'МБ', 'ГБ']:
            if size < 1024.0:
                return "%3.1f %s" % (size, unit)
            size /= 1024.0
        return "%3.1f %s" % (size, unit)

    '''Двойной клик'''
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

'''Обновление файловой системы в двух фреймах'''
def update_ful():
    global file_manager2
    global file_manager3
    file_manager2.update_file_system()
    file_manager3.update_file_system()

'''Создание фреймов и списков файловых систем'''
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
