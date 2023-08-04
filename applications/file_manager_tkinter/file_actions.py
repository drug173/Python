# -*- coding: utf-8 -*-
"""
Created on Thu Jul  6 11:16:18 2023

@author: drug1
"""
import io
import tkinter as tk
import os
import zipfile
from tkinter import Menu, simpledialog, messagebox

import tkinter.font as tkFont
import subprocess
import shutil
import psutil
import pyautogui
import time
from tkinter import ttk
import asyncio
from PIL import Image, ImageTk
from tkinter import messagebox, filedialog
import views
buff = None
flag = False

file_manager22 = None
file_manager33 = None

class ContextMenu(Menu):
    def __init__(self, file_manager, parent, current_path, tear=False):
        super().__init__(parent, tearoff=tear)
        self.y = None
        self.x = None
        self.parent = parent
        self.file_manager = file_manager
        self.current_path = current_path

        self.add_command(label="Обновить", command=self.update_dir)


    def coordinate_set(self, x, y):
        self.x = x
        self.y = y

    def update_dir(self):
        self.file_manager.update_file_system()

    '''удаление файла'''

    def delete_file(self, file_path):
        try:
            os.remove(file_path)
            return True
        except Exception as e:
            messagebox.showerror("ОШИБКА УДАЛЕНИЯ", f"Ошибка, файл не удалён: {str(e)}")
            return False

    '''Удаление файлов'''

    def delete_files(self):
        if messagebox.askyesno("ВНИМАНИЕ!", f"Вы удаляете файл '{self.current_path}'!"):
            if self.delete_file(self.current_path):
                views.update_ful()

    '''Копирование файла'''
    def copy_file(self):
        ''' функция для копирования файла'''
        # заносим полный путь к файлу в буффер
        global buff
        buff = self.current_path
        #views.update_ful()

    '''перемещение файла'''
    def move_file_folder(self):
        global flag
        flag = True
        global buff
        buff = self.current_path
        #views.update_ful()



'''Класс контекстного меню окна'''
class DefoltContextMenu(ContextMenu):
    def __init__(self, file_manager, parent, current_path):
        super().__init__(file_manager, parent, current_path)
        global buff
        if buff:
            self.add_separator()
            self.add_command(label="Вставить", command=self.insert_files_folders)
        self.add_separator()
        self.add_command(label="Создать директорию", command=self.create_dir)

    def create_dir(self):
        ''' функция для создания новой директории в текущей'''
        dir_name = simpledialog.askstring("Новая директория", "Введите название новой директории")
        if dir_name:
            path = os.path.join(self.current_path, dir_name)
            if os.path.exists(path):
                messagebox.showinfo("Папка не создана", f"Папка: ' {dir_name} ' - уже существует.")
            else:
                try:
                    os.mkdir(path)
                except OSError:
                    messagebox.showwarning("Операция невозможна!", "Отказано в доступе.")
                else:
                    self.update_dir()
        self.update_dir()

        '''функция вставки файла  или папки из буфера обмена'''

    def insert_files_folders(self):
        global buff
        global flag
        global file_manager22
        global file_manager33
        if buff is None:
            return
        copy_obj = buff
        to_dir = self.current_path
        if os.path.isdir(copy_obj):
            try:
                shutil.copytree(copy_obj, os.path.join(to_dir, os.path.basename(copy_obj)))
                if flag:
                    shutil.rmtree(copy_obj)
                    buff = None
                    flag = False
                    views.update_ful()
            except Exception as e:
                messagebox.showwarning("Ошибка!", f"Папка не скопирована: {str(e)}")
        else:
            try:
                shutil.copy2(copy_obj, to_dir)
                if flag:
                    self.delete_file(copy_obj)
                    buff = None
                    flag = False
                    views.update_ful()
            except Exception as e:
                messagebox.showwarning("Ошибка!", f"Файл не скопирован: {str(e)}")
        self.update_dir()


    '''Функция удаления папки'''
    def delete_folder(self):
        if messagebox.askyesno("Внимание!",
                               f"Вы хотите удалить папку '{self.current_path}' и всё содержимое?"):
            if self.delete_folder_with_content(self.current_path):
                views.update_ful()

    def delete_folder_with_content(self, folder_path):
        try:
            shutil.rmtree(folder_path)
            return True
        except Exception as e:
            messagebox.showerror("ОШИБКА", f"Ошибка удаления папки: {str(e)}")
            return False

    '''Функция копирования папки'''

    def copy_folder(self):
        global buff
        buff = self.current_path
        views.update_ful()


'''Класс контекстного меню папки'''
class FolderContextMenu(DefoltContextMenu):
    def __init__(self, file_manager, parent, current_path):
        super().__init__(file_manager, parent, current_path)
        # Добавляем разделитель
        self.add_command(label="Переименовать", command=self.rename_folder)
        self.add_command(label="Копировать", command=self.copy_folder)
        self.add_command(label="Вырезать", command=self.move_file_folder)
        self.add_separator()
        self.add_command(label="Удалить", command=self.delete_folder)

    def rename_folder(self):
        self.show_rename_entry(self.x, self.y)

    def show_rename_entry(self, x, y):
        self.entry_var = tk.StringVar()
        self.entry = tk.Entry(self.parent, textvariable=self.entry_var)

        foldername1 = os.path.basename(self.current_path)

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
        new_path = os.path.join(os.path.dirname(self.current_path), new_name)
        try:
            os.rename(self.current_path, new_path)
            self.update_dir()
            # messagebox.showinfo("Успех", "Файл успешно переименован.")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось переименовать файл: {e}")

        self.entry.destroy()  # Удаляем поле ввода
        self.entry = None  # Убираем ссылку на поле ввода
        views.update_ful()

'''Класс контекстного меню файла'''
class FileContextMenu(ContextMenu):
    def __init__(self, file_manager, parent, current_path):
        super().__init__(file_manager, parent, current_path)

        # Добавляем разделитель
        self.add_command(label="Переименовать", command=self.rename_file)
        self.add_command(label="Копировать", command=self.copy_file)
        self.add_command(label="Вырезать", command=self.move_file_folder)
        self.add_separator()
        self.add_command(label="Удалить", command=self.delete_files)

    def rename_file(self):
        self.show_rename_entry(self.x, self.y)

    def show_rename_entry(self, x, y):
        self.entry_var = tk.StringVar()
        self.entry = tk.Entry(self.parent, textvariable=self.entry_var)

        file_name = os.path.basename(self.current_path)
        file_extension = os.path.splitext(file_name)[1]
        file_name1 = os.path.splitext(file_name)[0]
        column_width = self.parent.column("#0", option="minwidth")  # Получаем минимальную ширину столбца
        text_width = self.parent.bbox(self.parent.selection(), column="#0")[2] - column_width
        text_width += 10  # Добавляем небольшой отступ

        self.entry.config(width=int(text_width // 7))  # Подберите подходящий коэффициент

        self.entry.insert(0, file_name1)
        #self.entry.insert(tk.END, file_extension)
        self.entry.bind("<Return>", self.save_renamed_file)
        self.entry.bind("<FocusOut>", self.save_renamed_file)
        self.entry.place(x=x, y=y, anchor="w")
        self.entry.focus_set()

    def save_renamed_file(self, event):
        new_name = self.entry_var.get()
        current_extension = os.path.splitext(self.current_path)[1]
        new_path = os.path.join(os.path.dirname(self.current_path), new_name + current_extension)
        try:
            os.rename(self.current_path, new_path)
            self.update_dir()
            #messagebox.showinfo("Успех", "Файл успешно переименован.")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось переименовать файл: {e}")

        self.entry.destroy()  # Удаляем поле ввода
        self.entry = None  # Убираем ссылку на поле ввода
        views.update_ful()
