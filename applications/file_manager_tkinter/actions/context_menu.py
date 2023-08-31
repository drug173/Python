# -*- coding: utf-8 -*-
"""
Created on Thu Jul  6 11:16:18 2023

@author: drug1
"""
import tkinter as tk
import os
from tkinter import Menu, simpledialog

import shutil
from tkinter import ttk
from tkinter import messagebox
#from views import views
import sys
import threading
import asyncio
import send2trash  # для перемещения в корзину
import queue
import time

from actions.insert import Insert




# Увеличить максимальную глубину рекурсии (примерное значение)
new_recursion_limit = 10000
sys.setrecursionlimit(new_recursion_limit)

buff = []  # буфер хранения скопированного (скопированных элементов) элемента
flag = False  # Флаг на перемещение элементов
var_progress = None  # количество обработанных байт для прогресбара
check_hidden_var = None
# check_operating_var = None




class ContextMenu(Menu):
    def __init__(self,  frame1, window, parent, current_path, selected_items, tear=False):
        super().__init__(parent, tearoff=tear)
        self.y = None
        self.x = None  # координаты клика мышки
        self.window = window      # НАШЕ ОКНО
        self.frame1 = frame1  # Фрейм в котором происходит действие
        self.parent = parent  # По чему был клик (дерево или окно: treeview или canvas)
        self.current_path = current_path  # текущая папка ((откуда копируем))
        self.selected_items = selected_items  # кортеж выбранных файлов и папок
        self.path_name = None  # Полный путь до обрабатываемого элемента ((выделенный элемент))
        self.thread_running = False  # Флаг выполнения параллельного потока
        self.loop = asyncio.get_event_loop()  # Создаем один экземпляр asyncio цикла для всего приложения
        self.add_command(label="Обновить", command=self.update_dir)  # Обновление фрейма
        global buff
        self.queue = queue.Queue()  # Очередь задач для обновления интерфейса
        self.add_context()  # Создаём контекстное меню

    '''Контекстное меню'''

    def add_context(self):
        if self.selected_items == ():  # Если клик по пустому месту
            self.add_context_empty()
        elif len(self.selected_items) == 1:  # Если выбран один элемент
            self.add_context_item()
        elif len(self.selected_items) > 1:  # Если выбрано больше одного элемента
            self.add_context_selected_elements()

    """Контекстное меню если клик по пустому месту"""

    def add_context_empty(self):
        if buff:
            self.add_separator()
            self.add_command(label="Вставить", command=self.insert_items)
        self.add_separator()
        self.add_command(label="Создать директорию", command=self.create_dir)
        self.path_name = self.current_path

    """Контекстное меню если клик по одному элементу"""

    def add_context_item(self):
        file_name = self.parent.item(self.selected_items[0], "text")
        self.path_name = os.path.join(self.current_path, file_name)
        item_type = self.parent.set(self.selected_items[0], "Type")
        if file_name == ".." or file_name == "  СКРЫТАЯ ПАПКА":
            return
        if item_type != "Папка":  # Если выбран файл
            self.path_name = self.path_name + item_type  # Если файл, то путь к файлу
            self.add_context_file()
        if os.path.isdir(self.path_name):  # Если выбрана папка
            self.add_context_folder()

    """Контекстное меню если клик по файлу"""

    def add_context_file(self):
        self.add_separator()
        self.add_command(label="Переименовать файл", command=self.rename_file)
        self.add_command(label="Копировать файл", command=self.copy_file_folder)
        self.add_command(label="Вырезать файл", command=self.move_file_folder)
        self.add_separator()
        self.add_command(label="Удалить файл", command=self.delete_items)

    """Контекстное меню если клик по папке"""

    def add_context_folder(self):
        self.add_separator()
        self.add_command(label="Создать директорию", command=self.create_dir)
        if buff:
            self.add_separator()
            self.add_command(label="Вставить", command=self.insert_items)
        self.add_separator()
        self.add_command(label="Переименовать папку", command=self.rename_folder)
        self.add_command(label="Копировать папку", command=self.copy_file_folder)
        self.add_command(label="Вырезать папку", command=self.move_file_folder)
        self.add_separator()
        self.add_command(label="Удалить папку", command=self.delete_items)

    """Контекстное меню если клик по выделенным элементам"""

    def add_context_selected_elements(self):
        self.add_separator()
        self.add_command(label="Копировать выделенное", command=self.copy_file_folder)
        self.add_command(label="Вырезать выделенное", command=self.move_file_folder)
        self.add_separator()
        self.add_command(label="Удалить выделенное", command=self.delete_items)

    """ВСТАВКА Элементов"""
    def insert_items(self):
        global buff
        global flag
        if buff is None:  # если буфер пуст выходим
            return
        if flag:
            number_action = 1
        else:
            number_action = 2
        insert = Insert(self.window, self.frame1, self.current_path, buff, number_action, os.path.basename(
                os.path.dirname(buff[0])), self.path_name)
        insert.insert_items()
        flag = False  # флаг - отменяем перемещение
        buff = []    # Очищаем буфер

    def time_get(self, time_start):
        time_end = time.time()
        if time_end - time_start > 1.5:
            time_start = time_end
            self.update_dir()

            return time_start
        else:
            return time_start

    """Объём папки"""

    def get_folder_size(self, folder_path):
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(folder_path):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                total_size += os.path.getsize(file_path)
        return total_size

    """Объём выделенных элементов"""

    def get_selected_size(self, selected_path):
        total_size = 0
        for item_path1 in selected_path:
            item_path = os.path.join(self.current_path, item_path1)
            if os.path.isdir(item_path):
                item_path = os.path.join(self.current_path, item_path1)
                total_size = total_size + self.get_folder_size(item_path)
            else:
                item_path = os.path.join(self.current_path, item_path1)
                total_size = total_size + os.path.getsize(item_path)

        return total_size

    """Конвертирование Байт"""

    def get_size(self, byte_size):
        sizes = ["Б", "КБ", "МБ", "ГБ", "ТБ"]
        i = 0
        while byte_size >= 1024 and i < len(sizes) - 1:
            byte_size /= 1024.0
            i += 1
        return str(round(byte_size, 2)) + sizes[i]

    '''перемещение выделенных элементов'''

    def move_file_folder(self):
        global flag
        flag = True  # устанавливаем флаг на перемещение (для удаления после копирования)
        self.copy_items()  # Вызываем копирование

    def copy_file_folder(self):
        global flag
        flag = False  # устанавливаем флаг на отмену перемещения (если был ранее установлен)
        self.copy_items()  # Вызываем копирование

    '''Копирование выделенных элементов'''

    def copy_items(self):
        global buff
        buff = []
        for item in self.selected_items:  # проходим циклом по кортежу выделенных элементов
            item_name = self.parent.item(item, "text")
            type1 = self.parent.set(item, "Type")
            if type1 != "Папка":  # если файл, заносим путь к файлу в список
                item_name = item_name + type1
                item_name = os.path.join(self.current_path, item_name)
                buff.append(item_name)
            if type1 == "Папка":  # Если папка, заносим путь к папке в список
                item_name = os.path.join(self.current_path, item_name)
                buff.append(item_name)
        #self.update_ful()

    '''Удаление выделенных элементов'''

    def delete_items(self):
        if self.thread_running:
            return
        self.selected_items = self.parent.selection()
        print("DELETE ", self.selected_items)
        if not self.selected_items:  # Если ничего не выбрано
            messagebox.showinfo("Ошибка", "Выберите элементы для удаления")
            return
        if not flag:  # Если не выбрано перемещение объектов
            confirmation_message = ""
            if len(self.selected_items) == 1:
                if os.path.isdir(self.path_name):
                    confirmation_message = f"Вы удаляете папку '{self.path_name}'!"
                else:
                    confirmation_message = f"Вы удаляете файл '{self.path_name}'!"
            elif len(self.selected_items) > 1:
                confirmation_message = "Вы удаляете выделенные элементы!"

            result = messagebox.askyesno("ВНИМАНИЕ!", confirmation_message)
            if result:  # Пользователь нажал "Да"
                thread1 = threading.Thread(target=self.delete_thread)
                thread1.start()

    #  Процесс удаления
    def delete_thread(self):

        self.thread_running = True
        items_to_delete = self.selected_items
        selected_file_folders_names = []
        for item in self.selected_items:
            file_name = self.parent.item(item, "text")
            type1 = self.parent.set(item, "Type")
            if type1 != "Папка":
                file_name = file_name + type1
            selected_file_folders_names.append(file_name)
        size_selected_items = self.get_selected_size(selected_file_folders_names)  # Размер всех удаляемых объектов
        progress_window = ProgressWindow(self.parent, self.frame1, 0, self.get_size(size_selected_items),
                                         self.path_name,
                                         selected_file_folders_names[0])  # Создаем окно процесса удаления
        progress_window.protocol("WM_DELETE_WINDOW", progress_window.on_closing)  # Добавляем обработчик закрытия окна
        size_item = 0

        start_time = time.time()
        for item in selected_file_folders_names:  # Создаём задачи на удаление из списка элементов на удаление
            if progress_window.closing:  # Проверяем, не закрывается ли окно
                break  # Останавливаем удаление, если окно закрывается
            item_list = [item]
            size_item = size_item + self.get_selected_size(item_list)  # Размер уже удалённых объектов
            if size_selected_items == 0:
                size = 0
            else:
                size = size_item * 100 / size_selected_items

            if self.window.check_operating_var:
                self.perform_deletion_quick(item, progress_window, size)  # Если быстрые операции
            else:
                self.perform_deletion(item, progress_window, size)  # Если удаление в цикле
            start_time = self.time_get(start_time)  # обновляем окно если время прошло больше 2 сек
        self.thread_running = False

        self.update_ful()  # обновляем окно
        if progress_window and progress_window.winfo_exists():
            try:
                if progress_window:
                    progress_window.destroy()  # Закрываем окно процесса удаления после завершения
            except Exception as e:
                messagebox.showwarning("Ошибка!", f"При закрытии окна: {str(e)}")

    #  Задача на удаление  элемента из списка выделенных элементов  (в цикле)
    def perform_deletion(self, item_name, progress_window, j):
        if os.path.isfile(item_name):  # если в списке выделенных элементов файл, то удаляем файл
            item_path = os.path.join(self.current_path, item_name)
            progress_window.var_name_item.set(item_path)
            result = self.delete_file1(item_path)
        else:  # если в списке выделенных элементов папка, то запускаем удаление папки и всех подпапок в цикле os.walk(source_folder):
            item_path = os.path.join(self.current_path, item_name)
            result = self.delete_folder_with_content2(item_path, progress_window)
        progress_window.current_progress.set(j)
        progress_window.update_progress()
        # progress_window.update()  # Обновляем интерфейс явно
        return result

    def delete_folder_with_content2(self, item, progress_window):
        source_folder = item
        for root, dirs, files in os.walk(source_folder):
            for file in files:
                file_path = os.path.join(root, file)
                progress_window.var_name_item.set(file_path)
                progress_window.update_progress()
                send2trash.send2trash(file_path)
        # После удаления файлов и папок внутри текущей папки, удаляем пустые папки
        try:
            # os.rmdir(folder_path)
            send2trash.send2trash(item)
            return f"Папка {item} успешно удалена"
        except Exception as e:
            return f"Ошибка при удалении папки {item}: {str(e)}"

    #  Задача на  быстрое удаление элемента из списка выделенных элементов
    def perform_deletion_quick(self, item_name, progress_window, j):
        if os.path.isfile(item_name):
            item_path = os.path.join(self.current_path, item_name)
            progress_window.var_name_item.set(item_path)
            result = self.delete_file1(item_path)
        else:
            item_path = os.path.join(self.current_path, item_name)
            progress_window.var_name_item.set(item_path)
            result = self.delete_folder_with_content1(item_path)
        progress_window.current_progress.set(j)
        progress_window.update_progress()
        # progress_window.update()  # Обновляем интерфейс явно
        return result

    def delete_file1(self, file_path):
        try:
            # os.remove(file_path)
            send2trash.send2trash(file_path)
            return f"Файл {file_path} успешно удален"
        except Exception as e:
            return f"Ошибка при удалении файла {file_path}: {str(e)}"

    def delete_folder_with_content1(self, folder_path):
        try:
            # os.rmdir(folder_path)
            send2trash.send2trash(folder_path)
            return f"Папка {folder_path} успешно удалена"
        except Exception as e:
            return f"Ошибка при удалении папки {folder_path}: {str(e)}"

    '''Переименовывание файла'''

    def rename_file(self):
        self.show_rename_entry(self.x, self.y)

    def show_rename_entry(self, x, y):
        self.entry_var = tk.StringVar()
        self.entry = tk.Entry(self.parent, textvariable=self.entry_var)

        file_name = os.path.basename(self.path_name)
        file_extension = os.path.splitext(file_name)[1]
        file_name1 = os.path.splitext(file_name)[0]
        column_width = self.parent.column("#0", option="minwidth")  # Получаем минимальную ширину столбца
        text_width = self.parent.bbox(self.parent.selection(), column="#0")[2] - column_width
        text_width += 10  # Добавляем небольшой отступ

        self.entry.config(width=int(text_width // 7))  # Подберите подходящий коэффициент

        self.entry.insert(0, file_name1)
        # self.entry.insert(tk.END, file_extension)
        self.entry.bind("<Return>", self.save_renamed_file)
        self.entry.bind("<FocusOut>", self.save_renamed_file)
        self.entry.place(x=x, y=y, anchor="w")
        self.entry.focus_set()

    def save_renamed_file(self, event):
        new_name = self.entry_var.get()
        current_extension = os.path.splitext(self.path_name)[1]
        new_path = os.path.join(os.path.dirname(self.path_name), new_name + current_extension)
        try:
            os.rename(self.path_name, new_path)
            self.update_dir()
            # messagebox.showinfo("Успех", "Файл успешно переименован.")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось переименовать файл: {e}")
        self.entry.destroy()  # Удаляем поле ввода
        self.entry = None  # Убираем ссылку на поле ввода
        self.update_ful()

    '''Копирование файла'''
    def copy_file(self):
        '''функция для копирования файла'''
        # заносим полный путь к файлу в буффер
        global buff
        buff = [self.path_name]
        # views.update_ful()

    # Координаты клика кнопкой мыши
    def coordinate_set(self, x, y):
        self.x = x
        self.y = y

    # Обновление фрейма
    def update_dir(self):
        self.frame1.update_file_system()

    def create_dir(self):
        ''' функция для создания новой директории в текущей'''
        dir_name = simpledialog.askstring("Новая директория", "Введите название новой директории")
        if dir_name:
            path = os.path.join(self.path_name, dir_name)
            if os.path.exists(path):
                messagebox.showinfo("Папка не создана", f"Папка: ' {dir_name} ' - уже существует.")
            else:
                try:
                    os.mkdir(path)
                except OSError:
                    messagebox.showwarning("Операция невозможна!", "Отказано в доступе.")
                else:
                    self.update_dir()
        self.update_ful()






    '''Переименовывание папки'''

    def rename_folder(self):
        self.show_rename_entry1(self.x, self.y)

    def show_rename_entry1(self, x, y):
        self.entry_var = tk.StringVar()
        self.entry = tk.Entry(self.parent, textvariable=self.entry_var)
        foldername1 = os.path.basename(self.path_name)
        column_width = self.parent.column("#0", option="minwidth")  # Получаем минимальную ширину столбца
        text_width = self.parent.bbox(self.parent.selection(), column="#0")[2] - column_width
        text_width += 10  # Добавляем небольшой отступ
        self.entry.config(width=int(text_width // 7))  # Подберите подходящий коэффициент
        self.entry.insert(0, foldername1)
        self.entry.bind("<Return>", self.save_renamed_folder)
        self.entry.bind("<FocusOut>", self.save_renamed_folder)
        self.entry.place(x=x, y=y, anchor="w")
        self.entry.focus_set()

    def save_renamed_folder(self, event):
        new_name = self.entry_var.get()
        new_path = os.path.join(os.path.dirname(self.path_name), new_name)
        try:
            os.rename(self.path_name, new_path)
            self.update_dir()
            # messagebox.showinfo("Успех", "Файл успешно переименован.")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось переименовать папку: {str(e)}")
        self.entry.destroy()  # Удаляем поле ввода
        self.entry = None  # Убираем ссылку на поле ввода
        self.update_ful()

    def update_ful(self):

        self.window.file_manager2.update_file_system()
        self.window.file_manager3.update_file_system()


class ProgressWindow(tk.Toplevel):
    def __init__(self, parent, frame, number_action, size_selected_items, path_name_in, path_name_out):
        super().__init__(parent)
        self.parent = parent
        self.frame = frame
        self.current_progress = tk.DoubleVar()  # значение прогресбара
        self.current_progress.set(0.01)  # Текущее значение прогресбара
        self.old_current_value = 0  # прошлое значение прогресбара
        self.var_percent_process = tk.DoubleVar()  # значение процентов обработанного элемента
        self.var_percent_process.set(0)
        if number_action == 0:  # Если действие удаления
            self.name_action = "удаления"
            self.name_action_2 = "удаляется "
        elif number_action == 1:  # Если действие перемещения
            self.name_action = "перемещения"
            self.name_action_2 = "перемещается "
        elif number_action == 2:  # если действие копирования
            self.name_action = "копирования"
            self.name_action_2 = "копируется "
        else:
            self.name_action = " "
            self.name_action_2 = " "
        self.title("Процесс " + self.name_action + " - " + str(self.current_progress.get()) + "%")
        self.geometry("400x200")  # Установка размера всплывающего окна
        self.resizable(False, True)

        self.var_name_item = tk.StringVar()  # Имя обрабатываемого объекта

        self.label3 = tk.Label(self, text=self.name_action_2 + " из:  " + path_name_out)
        self.label3.pack(anchor="w", padx=10, pady=(5, 0))  # Отступ сверху, без отступа снизу
        if number_action != 0:
            self.label4 = tk.Label(self, text=self.name_action_2 + " в:    " + os.path.basename(path_name_in))
            self.label4.pack(anchor="w", padx=10, pady=(1, 0))

        self.label = tk.Label(self, text="Всего " + self.name_action_2 + size_selected_items)
        self.label.pack(anchor="w", padx=10, pady=(1, 0))

        self.progressbar = ttk.Progressbar(self, mode="determinate", maximum=100, variable=self.current_progress)
        self.progressbar.pack(fill="x", padx=15, pady=5)  # Заполнить по горизонтали с отступами
        self.var_name_item.set("Начало процесса...")

        self.label2 = tk.Label(self, text=self.var_name_item.get(), anchor="w", justify="left")
        self.label2.pack(anchor="w", padx=10, pady=(1, 0))  # Отступ сверху, без отступа снизу
        self.update()
        self.update_progress()
        self.closing = False  # Флаг, указывающий на закрытие окна

    def update_progress(self):
        new_value = 0
        self.old_current_value = self.current_progress.get()

        if self.old_current_value < self.current_progress.get():  # Если старое значение прогрессбара не равно текущему, присваиваем текущее значение
            self.old_current_value = self.current_progress.get()

            new_value = self.old_current_value  # Новое значение прогресбара
            self.current_progress.set(new_value)

        self.update()

        if self.current_progress.get() <= 100:
            self.after(100, self.update_label_text)
            self.after(100, self.update_progress)
        else:
            self.destroy()
            return

    def update_label_text(self):
        try:
            if self.winfo_exists():  # Проверяем, существует ли окно
                self.title("Процесс " + self.name_action + " - " + str(round(self.current_progress.get(), 1)) + "%")
                # self.after(2000, self.frame.update_dir)
                if self.var_name_item.get():
                    self.label2.config(text=self.var_name_item.get())
                else:
                    self.label2.config(text="Имя объекта")
                self.update_idletasks()  # Обновляем все задачи
        except Exception as e:
            return

    def on_closing(self):
        self.closing = True  # Устанавливаем флаг закрытия
        self.destroy()  # Закрываем окно






