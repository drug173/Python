# -*- coding: utf-8 -*-
"""
Created on Thu Jul  6 11:15:58 2023

@author: drug1
"""

import ctypes
from ctypes import wintypes
import win32api
import win32gui
import os
import sys
import psutil
import tkinter
from tkinter import ttk
import tkinter as tk
from PIL import Image, ImageTk
import win32com.client
from actions.context_menu import ContextMenu
from actions.action import get_size

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

    def __init__(self, window, canvas):

        self.file_context_menu = None
        self.defolt_context_menu = None
        self.folder_context_menu = None
        self.window = window                # Само Окно
        self.context_menu = None
        self.selected_items = []
        self.item_path = None
        self.selecting = False   # Переменные для отслеживания выделения
        self.start_item = None
        self.end_item = None
        self.selected_file_folders_names = []
        self.drive_letter = self.get_drives()[0][0]
        self.current_path = self.get_drives()[0]
        self.parent_dir = self.get_drives()[0]
        self.icon_set()
        self.path_text = tkinter.StringVar()
        self.path_text.set(self.current_path)
        self.canvas = canvas
        # back button
        self.up_frame = ttk.Frame(self.canvas)
        self.up_frame.pack(fill="x")
        self.icon_width = 14  # Желаемая ширина кнопки и иконки
        self.icon_height = 12  # Желаемая высота кнопки и иконки
        self.back_button = tk.Button(self.up_frame, text="..", image=self.left_icon, command=self.on_up_click,
                                     width=self.icon_width, height=self.icon_height)
        self.back_button.pack(side='left', padx=2, pady=2)

        # self.back_button = tkinter.Button(self.up_frame, text="..", image=self.left_icon, command=self.parent_dir, width=1, height=1)
        # self.back_button.pack(side='left')

        self.path_label = tkinter.Entry(self.up_frame, textvariable=self.path_text,  state='readonly')
        self.path_label.pack(side=tk.RIGHT, fill=tk.X, expand=True)

        self.tree_frame = ttk.Frame(self.canvas)
        self.tree_frame.pack(fill="both", expand=True)
        self.treeview = self.create_tree(self.tree_frame)  # создание дерева файлов
        self.treeview.pack(fill="both", expand=True)
        self.scrollbar = ttk.Scrollbar(self.treeview, orient="vertical", command=self.treeview.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.treeview.config(yscrollcommand=self.scrollbar.set)  # Привязка скролбара к дереву
        self.binding()


    '''События мыши'''

    # Привязываем обработчики к событиям мыши
    def binding(self):
        self.context_menu_binding()
        #self.treeview.bind("<Button-1>", self.on_treeview_click)
        #self.treeview.bind("<B1-Motion>", self.on_treeview_drag)
        #self.treeview.bind("<ButtonRelease-1>", self.on_treeview_release)
        self.treeview.bind('<<TreeviewSelect>>', self.on_treeview_select)
        self.treeview.bind('<Double-Button-1>', self.on_double_click)

    # Вызов контекстного меню
    def context_menu_binding(self):
        self.treeview.bind("<Button-3>", self.show_context_menu)
        self.tree_frame.bind("<Button-3>", self.show_context_menu)

    '''Выделение элементов'''
    def check_selection(self):   # Убираем выделение ненужных элементов
        selected_items = self.treeview.selection()
        if selected_items:
            selected_item = selected_items[0]
            item_text = self.treeview.item(selected_item, "text")
            if item_text == ".." or item_text == "  СКРЫТАЯ ПАПКА":
                self.treeview.selection_remove(selected_item)
    def on_treeview_select(self, event):
        selected_items = self.treeview.selection()
        if selected_items:
            selected_item = selected_items[0]
            item_text = self.treeview.item(selected_item, "text")
            if item_text == ".." or item_text == "  СКРЫТАЯ ПАПКА":
                self.treeview.after(250, self.check_selection)  # Если выбран не нужный элемент удаляем из выделенных
                return
            if event.state == 0x4:  # 0x4 соответствует зажатой кнопке Ctrl
                if selected_item in self.selected_items:  # Если элемент уже выбран
                    self.treeview.selection_remove(selected_item)
                    self.selected_items.remove(selected_item)
                else:
                    self.treeview.selection_add(selected_item)    # Если элемент ещё не был выбран
                    self.selected_items.append(selected_item)
            else:
                self.selected_items = selected_items  # Если выбран один элемент
        # print("SELECT ", self.selected_items)

    '''КОНТЕКСТНОЕ МЕНЮ'''

    # функция вызова Контекстного меню
    def show_context_menu(self, event):
        try:  # получаем координаты клика правой кнопкой
            item = self.treeview.identify("item", event.x, event.y)
        except:
            item = None
        #self.on_treeview_select(event)
        if item:  # Если клик правой кнопкой по элементу
            #self.on_treeview_select(event)
            action_field = self.treeview
            if item not in self.selected_items:  # Если клик правой кнопкой не по выделенному элементу
                self.treeview.selection_set(item)  # Выделяем элемент по которому был клик правой кнопкой
                self.selected_items = (item,)
        else:
            self.selected_items = ()
            action_field = self.canvas
        self.context_menu = ContextMenu(self, self.window, action_field, self.current_path, self.selected_items)
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

    '''СОЗДАНИЕ ДЕРЕВА'''

    # Дерево
    def create_tree(self, parent1):
        # Создание дерева
        self.treeview = ttk.Treeview(parent1, columns=("Type", "Size"))
        self.treeview.heading("#0", text="Имя файла/папки", anchor='w')
        self.treeview.heading("Size", text="Размер")
        self.treeview.heading("Type", text="Тип")

        self.treeview.column("#0")
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

        files = [os.path.join(path, f) for f in files_and_folders if os.path.isfile(os.path.join(path, f))]
        folders = [os.path.join(path, f) for f in files_and_folders if os.path.isdir(os.path.join(path, f))]
        return files, folders

    """Вставка в дерево"""
    def insert_update_tree(self, path_name):
        if os.path.isdir(self.current_path):
            try:

                if os.path.isdir(path_name):
                    # print("Папка ", path_name)
                    folder_name = os.path.basename(path_name)
                    file_name_ful = os.path.join(self.current_path, folder_name)
                    icon = self.get_icon_defolt(file_name_ful)
                    self.treeview.insert('', 'end', text=folder_name, image=icon, values=("Папка", ""))
                else:
                    # print("Файл ", path_name)
                    file_name = os.path.basename(path_name)
                    file_extension = os.path.splitext(file_name)[1]
                    file_name1 = os.path.splitext(file_name)[0]
                    file_name_ful = os.path.join(self.current_path, file_name)

                    file_size = get_size(os.path.getsize(file_name_ful))
                    icon = self.get_icon_defolt(file_name_ful)
                    # print("PRINT   !!!!")
                    self.treeview.insert('', 'end', text=file_name1, image=icon, values=(file_extension, file_size))
            except PermissionError:
                self.path_text.set("скрытая папка ||  " + self.current_path)
                self.treeview.insert('', 'end', text="  СКРЫТАЯ ПАПКА", image=self.left_icon)


    # первоначальная загрузка файловой системы
    def load_file_system(self):
        try:
            files, folders = self.get_files_and_folders(self.current_path)
            for folder in folders:
                self.insert_update_tree(folder)

            for file in files:
                self.insert_update_tree(file)

        except PermissionError:
             self.treeview.insert('', 'end', text="  СКРЫТАЯ ПАПКА", image=self.left_icon)

    # Обновление файловой системы
    def update_file_system(self):
        if os.path.isdir(self.current_path):
            try:
                self.treeview.delete(*self.treeview.get_children())
                files, folders = self.get_files_and_folders(self.current_path)
                # parent_path = os.path.abspath(os.path.join(self.current_path, os.pardir))
                if not os.path.ismount(self.current_path):
                    self.treeview.insert('', 'end', text="..", image=self.left_icon, values=("",))
                for folder in folders:
                    self.insert_update_tree(folder)

                for file in files:
                    self.insert_update_tree(file)

            except PermissionError:
                self.path_text.set("скрытая папка ||  " + self.current_path)
                self.treeview.insert('', 'end', text="  СКРЫТАЯ ПАПКА", image=self.left_icon)

    def update_dir(self):
        self.update_file_system()

    # '''Метод для получения размера файла в удобочитаемом формате'''
    # def get_size(self, file_path):
    #     size = os.path.getsize(file_path)
    #     for unit in ['Б', 'КБ', 'МБ', 'ГБ']:
    #         if size < 1024.0:
    #             return "%3.1f %s" % (size, unit)
    #         size /= 1024.0
    #     return "%3.1f %s" % (size, unit)

    """Если клик по стрелке назад"""
    def on_up_click(self):

        self.parent_dir = os.path.abspath(os.path.join(self.current_path, os.pardir))
        if os.path.exists(self.parent_dir):  # Проверяем, существует ли родительский каталог
            self.current_path = self.parent_dir  # переходим на папку выше, и делаем её текущей
            self.path_text.set(self.current_path)  # Устанавливаем текущкю папку в надпись
        self.update_file_system()

    '''Двойной клик'''

    def on_double_click(self, event):
        selected_items = self.treeview.selection()
        if selected_items:
            selected_item = selected_items[0]

            item_text = self.treeview.item(selected_item, "text")

            if item_text == "  СКРЫТАЯ ПАПКА":
                parent_dir = os.path.abspath(os.path.join(self.current_path, os.pardir))
                self.current_path = parent_dir   # переходим на папку выше, и делаем её текущей
                self.path_text.set(self.current_path)  # Устанавливаем текущкю папку в надпись
            if item_text == "..":  # Проверяем, выбран ли элемент с двумя точками
                # Переходим на уровень выше

                self.parent_dir = os.path.abspath(os.path.join(self.current_path, os.pardir))
                if os.path.exists(self.parent_dir):  # Проверяем, существует ли родительский каталог
                    self.current_path = self.parent_dir    # переходим на папку выше, и делаем её текущей
                    self.path_text.set(self.current_path)   # Устанавливаем текущкю папку в надпись
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



