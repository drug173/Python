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
import win32api
import win32con
import win32gui
import sys
import ctypes
from ctypes import wintypes
from PIL import Image, ImageTk, ImageGrab
import win32com.client
import matplotlib.pyplot as plt
from tkinterdnd2 import DND_FILES, TkinterDnD
from file_actions import ContextMenu
import file_actions

file_manager2 = None
file_manager3 = None


class ICONINFO(ctypes.Structure):
    _fields_ = [
        ("fIcon", ctypes.c_bool),
        ("xHotspot", wintypes.DWORD),
        ("yHotspot", wintypes.DWORD),
        ("hbmMask", wintypes.HBITMAP),
        ("hbmColor", wintypes.HBITMAP),
    ]


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

        self.path_text = tkinter.StringVar()
        self.path_text.set(self.label_text)
        self.path_label = tkinter.Entry(self.frame, textvariable=self.path_text, width=40, state='readonly')
        self.path_label.pack(fill=tk.BOTH)



        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.treeview = self.create_tree(self.canvas)
        self.treeview.pack(fill=tk.BOTH, expand=True)
        self.selected_file_folders_names = []
        self.binding()

    '''События мыши'''

    # Привязываем обработчики к событиям мыши
    def binding(self):
        self.context_menu1()
        #self.treeview.bind("<Button-1>", self.on_treeview_click)
        #self.treeview.bind("<B1-Motion>", self.on_treeview_drag)
        #self.treeview.bind("<ButtonRelease-1>", self.on_treeview_release)
        self.treeview.bind('<<TreeviewSelect>>', self.on_treeview_select)
        self.treeview.bind('<Double-Button-1>', self.on_double_click)

    # Вызов контекстного меню
    def context_menu1(self):
        self.treeview.bind("<Button-3>", self.show_context_menu)
        self.canvas.bind("<Button-3>", self.show_context_menu)

    '''Выделение элементов'''

    def on_treeview_select(self, event):
        if event.state == 0x4:  # 0x4 соответствует зажатой кнопке Ctrl
            selected_item = self.treeview.selection()[0]
            if selected_item in self.selected_items:
                self.treeview.selection_remove(selected_item)
                self.selected_items.remove(selected_item)
            else:
                self.treeview.selection_add(selected_item)
                self.selected_items.append(selected_item)
        else:
            self.selected_items = self.treeview.selection()

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
                file_name = file_name + type1
            self.selected_file_folders_names.append(file_name)

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


    def on_treeview_press(self, event):
        self.start_item = self.treeview.identify_row(event.y)
        # Добавьте код для подготовки элемента к перетаскиванию




    '''КОНТЕКСТНОЕ МЕНЮ'''

    # функция вызова Контекстного меню
    def show_context_menu(self, event):
        try:  # получаем координаты клика правой кнопкой
            item = self.treeview.identify("item", event.x, event.y)
        except:
            item = None
        self.on_treeview_select(event)
        if item:  # Если клик правой кнопкой по элементу
            self.on_treeview_select(event)
            action_field = self.treeview
            if item not in self.selected_items:  # Если клик правой кнопкой не по выделенному элементу
                self.treeview.selection_set(item)  # Выделяем элемент по которому был клик правой кнопкой
                self.selected_items = (item,)
        else:
            self.selected_items = ()
            action_field = self.canvas
        self.context_menu = ContextMenu(self, action_field, self.current_path, self.selected_items)
        if action_field == self.treeview:
            x, y, _, _ = self.treeview.bbox(item)
            self.context_menu.coordinate_set(x + 36, y + 10)
        # self - передаём в функцию фрейм
        # action_field - по чему был клик (дерево или окно: treeview или canvas)
        # self.current_path - текущая папка
        # self.selected_items - кортеж выбранных файлов и папок
        self.context_menu.post(event.x_root, event.y_root)

    '''Очистка дерева перед обновлением'''

    def clear_tree(self, tree):
        tree.delete(*tree.get_children())

    '''ЗАГРУЗКА ИКОНОК'''

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

    '''ПОЛУЧЕНИЕ ИКОНОК'''

    #  Получение иконки системной, если нет то по умолчанию
    def get_icon_defolt(self, items_path):
        icon_path, icon_index = self.get_custom_folder_icon(items_path)  # проверяем есть ли системные иконки у папки
        # print("items_path ", items_path, icon_path)
        if not icon_path:  # Если системной иконки нет
            item_name = os.path.basename(items_path)
            file_extension = os.path.splitext(item_name)[1]

            if os.path.isfile(items_path):  # Если файл
                if file_extension in self.file_icons:
                    icon_path1 = self.file_icons[file_extension]
                else:
                    icon_path1 = self.default_file_icon
            else:  # если папка
                icon_path1 = self.folder_icon
        else:
            icon_path1 = self.path_index_to_icon(icon_path, icon_index)
            if not icon_path1:                    # НЕ ДОДЕЛАНО!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                icon_path1 = self.folder_icon
        return icon_path1

    #  Получение системной иконки папки (если есть)
    def get_custom_folder_icon(self, folder_path):
        desktop_ini_path = os.path.join(folder_path, 'desktop.ini')  # Получаем путь к файлу desktop.ini если есть файл
        icon_path = None
        icon_index = None
        if os.path.exists(desktop_ini_path):  # если есть файл desktop.ini
            with open(desktop_ini_path, 'r') as ini_file:  # ОТКРЫВАЕМ файл
                icon_path, icon_index = self.desktop_file_to_icon(
                    ini_file)  # Ищем в файле информацию об иконке для текущей папки в desktop.ini
        return icon_path, icon_index

    #  Получение данных об иконки текущей папки из desktop.ini
    def desktop_file_to_icon(self, ini_file):
        lines = ini_file.readlines()
        for line in lines:  # Проходим по файлу, ищем путь к файлу иконки и индекс
            if line.startswith('IconResource='):

                n, path_index = line.split('=')
                icon_path_index = path_index.strip()
                icon_path = icon_path_index.strip().split(',')[0]
                icon_index = int(icon_path_index.strip().split(',')[1])
                return icon_path, icon_index  # # Если найден путь прекращаем
        return None, None

    # Получение из пути к файлу  и индекса изображение иконки для текущей папки
    def path_index_to_icon(self, icon_path, icon_index):
        """

        Нужно доработать

        """
        if icon_path and icon_index is not None:  # Если путь есть
            path = None
            try:

                # self.desriptor_to_icon(folder_path)


                hicon = win32gui.ExtractIcon(win32api.GetModuleHandle(None), icon_path, icon_index)


                icon_info = win32gui.GetIconInfo(hicon)


                width = icon_info[1]
                height = icon_info[2]
                #print("width height ", width, height)

                #bmp_data = bytearray(icon_info[4].bmBits)[:width * height * 4]
                #bmp_image = Image.frombuffer("RGBA", (width, height), bmp_data, "raw", "BGRA", 0, 1)

                #print("image 45 ")
                return path
            except Exception as e:
                #print("Error loading icon:", e)
                return path

    """Извлечение метаданных файла"""

    def get_file_metadata(self, file_path):
        try:
            shell = win32com.client.Dispatch("Shell.Application")
            folder = shell.Namespace(os.path.dirname(file_path))
            file_item = folder.ParseName(os.path.basename(file_path))

            metadata = {}
            for i in range(266):
                prop_name = folder.GetDetailsOf(None, i)
                prop_value = folder.GetDetailsOf(file_item, i)
                if prop_value:
                    metadata[prop_name] = prop_value

            return metadata
        except Exception as e:
            print("Error:", e)
            return None

    '''СОЗДАНИЕ ДЕРЕВА'''

    # Дерево
    def create_tree(self, parent1):
        # Создание дерева
        self.treeview = ttk.Treeview(parent1, columns=("Type", "Size"))
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
                folder_name = os.path.basename(folder)
                file_name_ful = os.path.join(self.current_path, folder_name)
                icon = self.get_icon_defolt(file_name_ful)

                self.treeview.insert('', 'end', text=folder, image=icon, values=("Папка", ""))
            for file in files:
                file_name = os.path.basename(file)
                file_extension = os.path.splitext(file_name)[1]
                file_name1 = os.path.splitext(file_name)[0]
                file_name_ful = os.path.join(self.current_path, file_name)
                file_size = self.get_size(file_name_ful)

                icon = self.get_icon_defolt(file_name_ful)

                self.treeview.insert('', 'end', text=file_name1, image=icon, values=(file_extension, file_size))
        except PermissionError:
            self.treeview.insert('', 'end', text="  СКРЫТАЯ ПАПКА", image=self.left_icon, values=("Папка",))

    # Обновление файловой системы
    def update_file_system(self):
        if os.path.isdir(self.current_path):
            try:
                self.treeview.delete(*self.treeview.get_children())
                files, folders = self.get_files_and_folders(self.current_path)
                parent_path = os.path.abspath(os.path.join(self.current_path, os.pardir))
                if not os.path.ismount(self.current_path):
                    self.treeview.insert('', 'end', text="..", image=self.left_icon, values=("",))
                for folder in folders:
                    folder_name = os.path.basename(folder)
                    file_name_ful = os.path.join(self.current_path, folder_name)
                    icon = self.get_icon_defolt(file_name_ful)
                    self.treeview.insert('', 'end', text=folder, image=icon, values=("Папка", ""))
                for file in files:
                    file_name = os.path.basename(file)
                    file_extension = os.path.splitext(file_name)[1]
                    file_name1 = os.path.splitext(file_name)[0]
                    file_name_ful = os.path.join(self.current_path, file_name)
                    file_size = self.get_size(file_name_ful)
                    icon = self.get_icon_defolt(file_name_ful)

                    self.treeview.insert('', 'end', text=file_name1, image=icon, values=(file_extension, file_size))
            except PermissionError:
                self.path_text.set("(скрытая папка)   " + self.current_path)
                self.treeview.insert('', 'end', text="  СКРЫТАЯ ПАПКА", image=self.left_icon, values=("Папка",))


    def update_dir(self):
        self.update_file_system()

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
                #self.path_label.config(text=self.current_path)
                self.path_text.set(self.current_path)
            if item_text == "..":  # Проверяем, выбран ли элемент с двумя точками
                # Переходим на уровень выше

                self.parent_dir = os.path.abspath(os.path.join(self.current_path, os.pardir))
                if os.path.exists(self.parent_dir):  # Проверяем, существует ли родительский каталог
                    self.current_path = self.parent_dir
                    #self.path_label.config(text=self.current_path)
                    self.path_text.set(self.current_path)
            else:
                # Получаем полный путь элемента, добавляя его к текущему пути
                item_path = os.path.join(self.current_path, item_text)

                # Если выбрана папка, переходим в неё и обновляем содержимое
                if os.path.isdir(item_path) and not os.path.islink(item_path):
                    self.current_path = item_path

                    # Обновляем метку с текущим путем
                    #self.path_label.config(text=self.current_path + "\\")
                    self.path_text.set(self.current_path + "\\")
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
        #self.path_label.config(text=self.current_path)
        self.path_text.set(self.current_path)
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
        #self.path_label.config(text=self.current_path)
        self.path_text.set(self.current_path)
        self.update_file_system()


'''Обновление файловой системы в двух фреймах'''


def update_ful():
    global file_manager2
    global file_manager3
    file_manager2.update_file_system()
    file_manager3.update_file_system()


'''Создание фреймов и списков файловых систем'''


class Applications:
    def __init__(self, root, event=None):
        self.label = None  # Атрибут для хранения ссылки на виджет Label
        self.resized = False
        menu_bar = tk.Menu(root)
        self.root = root
        self.len_1 = self.root.winfo_width()
        root.config(menu=menu_bar)
        file_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="МЕНЮ", menu=file_menu)

        file_menu.add_command(label="Выход", command=root.quit)
        file_menu.add_separator()
        self.check_var = tk.BooleanVar()
        file_menu.add_checkbutton(label="Отображать скрытые объекты", variable=self.check_var)



        notebook = ttk.Notebook(root)
        notebook.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.tab1 = tk.Frame(notebook)
        self.tab2 = tk.Frame(notebook)
        self.tab3 = tk.Frame(notebook)
        notebook.add(self.tab1, text="Проводник")
        notebook.add(self.tab2, text="Tab 2")
        notebook.add(self.tab3, text="О программе")
        global file_manager2
        global file_manager3

        frame2 = tk.Frame(self.tab1, bg="lightgray")
        frame2.pack(side=tk.LEFT, padx=4, pady=4, fill=tk.BOTH, expand=True)

        frame3 = tk.Frame(self.tab1, bg="#A9A9A9")
        frame3.pack(side=tk.LEFT, padx=4, pady=4, fill=tk.BOTH, expand=True)

        file_manager2 = FileManagerList_2(frame2)
        file_manager3 = FileManagerList(frame3)
        root.bind("<Configure>", self.event_resize)
        self.set_text(self.len_1)
    def event_resize(self, event):
        if not self.resized:  # Проверяем, было ли уже изменение размера
            self.len_1 = self.root.winfo_width()
            self.label.configure(wraplength=self.len_1)
            self.label3.configure(wraplength=self.len_1)
            self.label4.configure(wraplength=self.len_1)
            #self.resized = True  # Устанавливаем флаг после вызова set_text

    """Текст для вкладки"""
    def set_text(self, len_1):
        current_directory = os.path.dirname(os.path.abspath(sys.argv[0]))
        path_folder = os.path.join(current_directory, "icons", "2.png")
        logo = tk.PhotoImage(file=path_folder)

        self.label = ttk.Label(self.tab3, image=logo, text="Файловый менеджер", font=("Arial", 16), compound="left", anchor='w', wraplength=len_1-80)
        self.label3= ttk.Label(self.tab3, text="Менеджер позволяет: копировать, удалять, переносить файлы.", font=("Arial", 12), anchor='w', wraplength=len_1-120)
        self.label4 = ttk.Label(self.tab3, text="Множественное выделение: Shift либо Ctrl+клик мышкой ", font=("Arial", 12), anchor='w', wraplength=len_1-120)

        self.label1 = ttk.Label(self.tab3, text="Разработка: Лейман М.А.", font=("Arial", 14))
        self.label2 = ttk.Label(self.tab3, text="email: leiman@sfedu.ru.", font=("Arial", 14))

        self.label.pack(fill=tk.X, padx=40)
        self.label3.pack(fill=tk.X, padx=20)
        self.label4.pack(fill=tk.X, padx=20)

        self.label2.pack(side=tk.BOTTOM)
        self.label1.pack(side=tk.BOTTOM)
        self.label.image = logo  # Сохраняем ссылку на объект PhotoImage
