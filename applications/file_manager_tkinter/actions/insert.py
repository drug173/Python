import ctypes
import shutil
import time
from ctypes import wintypes

import send2trash
import win32api
import win32gui
import os
import threading
import sys
import psutil
import tkinter
from tkinter import ttk, messagebox
from views.progressbar import ProgressWindow
from actions.action import get_selected_size, get_size

# Увеличить максимальную глубину рекурсии (примерное значение)
new_recursion_limit = 10000
sys.setrecursionlimit(new_recursion_limit)


import tkinter as tk
from PIL import Image, ImageTk
import win32com.client
# from actions.file_actions import ContextMenu
# from views.filemanager import FileManagerList, FileManagerList_2

class Insert:
    def __init__(self, window, frame1, current_path, buff, number_action, path_name_out, path_name_in):
        self.window = window   # НАШЕ ОКНО
        self.frame1 = frame1
        self.current_path = current_path   # Текущая папка
        self.buff = buff    # список выделенных элементов
        self.number_action = number_action  # НОМЕР действия  (копирование, перемещение, удаление)
        self.path_name_in = path_name_in   # Откуда копируем
        self.path_name_out = path_name_out  # Куда копируем
        self.size_selected_items = get_selected_size(self.current_path, self.buff)  # Размер выделенных элементов (в Байтах)
        self.size_item = 0   # Размер обработанных файлов
    '''Вставка выделенных элементов из буфера обмена'''

    def insert_items(self):

        if self.buff is None:  # если буфер пуст выходим
            return
        thread2 = threading.Thread(target=self.insert_thread1)
        thread2.start()

    def insert_thread1(self):
        print(" Что копируем 1", self.buff)
        copy_objects = self.buff
        progress_window = ProgressWindow(None, None, self.number_action,  get_size(self.size_selected_items), os.path.basename(self.path_name_in), os.path.basename(self.path_name_out))  # Создаём прогресбар
        progress_window.protocol("WM_DELETE_WINDOW", progress_window.on_closing)  # Добавляем обработчик закрытия окна
        progress_window.update()  # Обновляем интерфейс явно
        self.thread_running = True  # Устанавливаем флаг перед началом копирования
        self.size_item = 0
        start_time = time.time()
        for item in copy_objects:
            if progress_window.closing:  # Проверяем, не закрывается ли окно
                break  # Останавливаем копирование, если окно закрывается
            item_list = [item]
            progress_window.var_name_item.set(item)  # Устанавливаем название обрабатываемого элемента для прогресбара
            # size_item = size_item + get_selected_size(item_list)
            print("ФЛАГ 2 ", self.window.check_operating_var.get())
            if self.window.check_operating_var.get():             # ЕСЛИ быстрые операции
                self.size_item = self.size_item + get_selected_size(self.current_path, item_list)
                self.insert_files_folders_quick(item)  # Если быстрые операции
                print("Размер ", self.size_item)
                if self.size_selected_items == 0:  # Если объём выделенных элементов равен нулю (Пустая папка)
                    size = 0
                else:
                    size = self.size_item * 100 / self.size_selected_items  # Сколько уже обработано объектов (процент обработанных)
                progress_window.current_progress.set(size)
            else:              # ЕСЛИ ЦИКЛ
                print(" Size1 ", get_size(self.size_item))
                # print(" size_item ", self.size_item)
                size_1 =self.insert_files_folders(item, progress_window)
                print("SIZE!",  size_1)
                print(" Размер + ", get_size(size_1))
                print(" Size12 ", get_size(self.size_item))
        self.buff = None  # буфер очищаем
        self.update_ful()  # Обновляем все фреймы
        if progress_window and progress_window.winfo_exists():
            try:
                if progress_window:
                    progress_window.destroy()  # Закрываем окно процесса копирования после завершения
            except Exception as e:
                pass

    def insert_folders(self, item, progress_window):
        source_folder = item
        destination_folder = self.path_name_in   # КУДА КОПИРУЕМ
        print("Путь папки", source_folder, destination_folder)
        destination_dir_path = os.path.join(destination_folder, os.path.basename(source_folder))
        print(destination_dir_path)
        os.makedirs(destination_dir_path, exist_ok=True)  # Создаём первую папку куда копируем всё остальное
        for root, dirs, files in os.walk(source_folder):
            for dir in dirs:
                source_dir_path = os.path.join(root, dir)
                relative_dir_path = os.path.relpath(source_dir_path, source_folder)
                destination_dir_path1 = os.path.join(destination_dir_path, relative_dir_path)
                os.makedirs(destination_dir_path1, exist_ok=True)  # Создаем вложенные папки
            for file in files:
                source_file_path = os.path.join(root, file)
                relative_file_path = os.path.relpath(source_file_path, source_folder)
                destination_file_path = os.path.join(destination_dir_path, relative_file_path)

                progress_window.var_name_item.set(source_file_path)

                self.size_item = self.size_item + os.path.getsize(source_file_path)
                print("что  в РАБОТЕ+++ ", source_file_path)
                print("РАЗМЕР ", get_size(self.size_item))
                if self.size_selected_items == 0:
                    size = 0
                else:
                    size = self.size_item * 100 / self.size_selected_items
                shutil.copy2(source_file_path, destination_file_path)
                progress_window.current_progress.set(size)
                print("ПРОЦЕНТ ", size)
        return self.size_item

    def move_folders(self, item, progress_window):
        source_folder = item
        destination_folder = self.path_name_in   # Куда копируем
        print("Путь папки", source_folder, destination_folder)
        destination_dir_path = os.path.join(destination_folder, os.path.basename(source_folder))
        print(destination_dir_path)
        os.makedirs(destination_dir_path, exist_ok=True)  # Создаём первую папку куда копируем всё остальное
        for root, dirs, files in os.walk(source_folder):
            for dir in dirs:
                source_dir_path = os.path.join(root, dir)
                relative_dir_path = os.path.relpath(source_dir_path, source_folder)
                destination_dir_path1 = os.path.join(destination_dir_path, relative_dir_path)
                os.makedirs(destination_dir_path1, exist_ok=True)  # Создаем вложенные папки

                # self.frame1.insert_update_tree(destination_dir_path1)
            for file in files:
                source_file_path = os.path.join(root, file)
                relative_file_path = os.path.relpath(source_file_path, source_folder)
                destination_file_path = os.path.join(destination_dir_path, relative_file_path)

                # self.frame1.insert_update_tree(destination_file_path)
                progress_window.var_name_item.set(source_file_path)
                self.size_item = self.size_item + os.path.getsize(source_file_path)
                print("что  в РАБОТЕ+++ ", source_file_path)
                print("РАЗМЕР ", get_size(self.size_item))
                if self.size_selected_items == 0:
                    size = 0
                else:
                    size = self.size_item * 100 / self.size_selected_items
                shutil.move(source_file_path, destination_file_path)
                progress_window.current_progress.set(size)
            # После перемещения файлов и папок внутри текущей папки, удаляем пустые папки
        try:
            # os.rmdir(folder_path)
            send2trash.send2trash(item)
            return self.size_item
        except Exception as e:
            return f"Ошибка при удалении папки {item}: {str(e)}"

    # функция вставки файла или папки через цикл
    def insert_files_folders(self, item, progress_window):
        copy_obj = item  # что копируем
        print("Копирование в цикле ", item)
        to_dir = self.path_name_in  # куда копируем
        if os.path.isdir(copy_obj):      # Если папка
            try:
                if self.number_action==1:
                    self.size_item = self.size_item + self.move_folders(copy_obj, progress_window)
                    path_item = os.path.join(to_dir, os.path.basename(copy_obj))
                    self.frame1.insert_update_tree(path_item)
                    return self.size_item
                else:
                    self.size_item = self.size_item + self.insert_folders(copy_obj, progress_window)
                    print("self.size_item  66 ", self.size_item )
                    path_item = os.path.join(to_dir, os.path.basename(copy_obj))
                    self.frame1.insert_update_tree(path_item)
                    return self.size_item
            except FileExistsError:
                messagebox.showwarning("Ошибка!", "Папка уже существует.")
            except Exception as e:
                messagebox.showwarning("Ошибка!", f"Папка не скопирована: {str(e)}")
        else:        # Если файл
            try:
                if os.path.exists(os.path.join(to_dir, os.path.basename(copy_obj))):
                    messagebox.showwarning("Ошибка!", "Файл уже существует.")
                elif self.number_action==1:    # Если перемещение
                    self.size_item = self.size_item + os.path.getsize(copy_obj)
                    shutil.move(copy_obj, to_dir)
                    path_item = os.path.join(to_dir, os.path.basename(copy_obj))
                    self.frame1.insert_update_tree(path_item)
                    if self.size_selected_items == 0:
                        size = 0
                    else:
                        size = self.size_item * 100 / self.size_selected_items
                    progress_window.current_progress.set(size)
                    return self.size_item
                else:    # Если копирование
                    self.size_item = self.size_item + os.path.getsize(copy_obj)
                    shutil.copy2(copy_obj, to_dir)
                    path_item = os.path.join(to_dir, os.path.basename(copy_obj))
                    self.frame1.insert_update_tree(path_item)
                    print("ВСего размер", get_size(self.size_item))
                    if self.size_selected_items == 0:
                        size = 0
                    else:
                        size = self.size_item * 100 / self.size_selected_items
                    progress_window.current_progress.set(size)
                    return self.size_item
            except Exception as e:
                messagebox.showwarning("Ошибка!", f"Файл не скопирован: {str(e)}")

    # функция вставки файла или папки быстрая
    def insert_files_folders_quick(self, item):
        print(" быстрое копирование == ", item)
        copy_obj = item  # что копируем
        to_dir = self.path_name_in  # куда копируем
        if os.path.isdir(copy_obj):
            print("Что копируем", item)
            try:
                if self.number_action == 1:
                    path_item = os.path.join(to_dir, os.path.basename(copy_obj))
                    shutil.move(copy_obj, to_dir)
                    self.frame1.insert_update_tree(path_item)
                else:
                    path_item = os.path.join(to_dir, os.path.basename(copy_obj))
                    shutil.copytree(copy_obj, path_item)
                    self.frame1.insert_update_tree(path_item)

            except FileExistsError:
                messagebox.showwarning("Ошибка!", "Папка уже существует.")
            except Exception as e:
                messagebox.showwarning("Ошибка!", f"Папка не скопирована: {str(e)}")
        else:
            try:
                if os.path.exists(os.path.join(to_dir, os.path.basename(copy_obj))):
                    messagebox.showwarning("Ошибка!", "Файл уже существует.")
                elif self.number_action == 1:
                    shutil.move(copy_obj, to_dir)
                    path_item = os.path.join(to_dir, os.path.basename(copy_obj))
                    self.frame1.insert_update_tree(path_item)
                else:
                    shutil.copy2(copy_obj, to_dir)
                    path_item = os.path.join(to_dir, os.path.basename(copy_obj))
                    self.frame1.insert_update_tree(path_item)
            except Exception as e:
                messagebox.showwarning("Ошибка!", f"Файл не скопирован: {str(e)}")

    def update_ful(self):
        self.window.file_manager2.update_file_system()
        self.window.file_manager3.update_file_system()

