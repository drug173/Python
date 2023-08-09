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
import sys

# Увеличить максимальную глубину рекурсии (примерное значение)
new_recursion_limit = 10000
sys.setrecursionlimit(new_recursion_limit)


buff = None # буфер хранения скопированного (скопированных элементов) элемента
flag = False # Флаг на перемещение элементов




class ContextMenu(Menu):
    def __init__(self, frame1, parent, current_path, selected_items, tear=False):
        super().__init__(parent, tearoff=tear)
        self.y = None
        self.x = None # координаты клика мышки
        self.frame1 = frame1  # Фрейм в котором происходит действие
        self.parent = parent  # По чему был клик (дерево или окно: treeview или canvas)
        self.current_path = current_path  # текущая папка
        self.path_name = None  # Полный путь до обрабатываемого элемента
        self.selected_items = selected_items  # кортеж выбранных файлов и папок


        self.add_command(label="Обновить", command=self.update_dir) # Обновление фрейма
        global buff

        if self.selected_items == ():  # Если клик по пустому месту
            if buff:
                self.add_separator()
                self.add_command(label="Вставить", command=self.insert_items)
            self.add_separator()
            self.add_command(label="Создать директорию", command=self.create_dir)
            self.path_name = self.current_path
        if len(self.selected_items) == 1:  # Если выбран один элемент

            file_name = self.parent.item(self.selected_items[0], "text")

            self.path_name = os.path.join(self.current_path, file_name)
            item_type = self.parent.set(self.selected_items[0], "Type")
            if item_type!="Папка":  #  Если выбран файл
                self.path_name = self.path_name + item_type # Если файл, то путь к файлу

                self.add_separator()
                self.add_command(label="Переименовать файл", command=self.rename_file)
                self.add_command(label="Копировать файл", command=self.copy_file)
                self.add_command(label="Вырезать файл", command=self.move_file_folder)
                self.add_separator()
                self.add_command(label="Удалить файл", command=self.delete_files)
            if os.path.isdir(self.path_name):  # Если выбрана папка
                self.add_separator()
                self.add_command(label="Создать директорию", command=self.create_dir)
                if buff:
                    self.add_separator()
                    self.add_command(label="Вставить", command=self.insert_items)
                self.add_separator()
                self.add_command(label="Переименовать папку", command=self.rename_folder)
                self.add_command(label="Копировать папку", command=self.copy_folder)
                self.add_command(label="Вырезать папку", command=self.move_file_folder)
                self.add_separator()
                self.add_command(label="Удалить папку", command=self.delete_folder)

        if len(self.selected_items) > 1:  # Если выбрано больше одного элемента
            self.add_separator()
            self.add_command(label="Копировать выделенное", command=self.copy_items)
            self.add_command(label="Вырезать выделенное", command=self.move_items)
            self.add_separator()
            self.add_command(label="Удалить выделенное", command=self.delete_items)

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
            print("buff", buff)
        views.update_ful()

    '''перемещение выделенных элементов'''
    def move_items(self):
        pass

    '''Удаление выделенных элементов'''
    def delete_items(self):
        for item in self.selected_items: # проходим циклом по кортежу выделенных элементов
            item_name = self.parent.item(item, "text")
            type1 = self.parent.set(item, "Type")
            if type1 != "Папка":  # удаляем если выбрана не папка
                item_name = item_name + type1
                item_name = os.path.join(self.current_path, item_name)
                self.delete_file(item_name)
            if type1=="Папка":  # удаляем если выбрана папка
                item_name = os.path.join(self.current_path, item_name)
                self.delete_folder_with_content(item_name)
            print("удаление", item_name)
        views.update_ful()




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
        views.update_ful()

    def delete_file(self, file_path):
        try:
            os.remove(file_path)
            return True
        except Exception as e:
            messagebox.showerror("ОШИБКА УДАЛЕНИЯ", f"Ошибка, файл не удалён: {str(e)}")
            return False

    '''Удаление файлов'''

    def delete_files(self):
        if messagebox.askyesno("ВНИМАНИЕ!", f"Вы удаляете файл '{self.path_name}'!"):
            if self.delete_file(self.path_name):
                views.update_ful()

    '''Копирование файла'''

    def copy_file(self):
        ''' функция для копирования файла'''
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
        views.update_ful()

    '''Вставка выделенных элементов из буфера обмена'''
    def insert_items(self):
        global buff
        global flag
        if buff is None:  # если буфер пуст выходим
            return
        copy_objects = buff
        for item in copy_objects:
            self.insert_files_folders(item)
            views.update_ful()  # Обновляем все фреймы

        buff = None  # буфер очищаем
        flag = False  # флаг - отменяем перемещение
        views.update_ful()  # Обновляем все фреймы

    '''функция вставки файла  или папки'''
    def insert_files_folders(self, item):
        global flag
        copy_obj = item
        to_dir = self.path_name
        if os.path.isdir(copy_obj):
            try:
                shutil.copytree(copy_obj, os.path.join(to_dir, os.path.basename(copy_obj)))
                if flag:
                    shutil.rmtree(copy_obj)
            except FileExistsError:
                messagebox.showwarning("Ошибка!", "Папка уже существует.")
            except Exception as e:
                messagebox.showwarning("Ошибка!", f"Папка не скопирована: {str(e)}")
                print(str(e))
        else:
            try:

                if os.path.exists(os.path.join(to_dir, os.path.basename(copy_obj))):
                    messagebox.showwarning("Ошибка!", "Файл уже существует.")
                else:
                    shutil.copy2(copy_obj, to_dir)
                if flag:
                    self.delete_file(copy_obj)
            except Exception as e:
                messagebox.showwarning("Ошибка!", f"Файл не скопирован: {str(e)}")


    '''Функция удаления папки'''
    def delete_folder(self):
        if messagebox.askyesno("Внимание!", f"Вы хотите удалить папку '{self.path_name}' и всё содержимое?"):
            if self.delete_folder_with_content(self.path_name):
                views.update_ful()

    def delete_folder_with_content(self, folder_path):
        try:
            shutil.rmtree(folder_path)
            return True
        except Exception as e:
            messagebox.showerror("ОШИБКА", f"Ошибка удаления: {str(e)}")
            return False

    '''Функция копирования папки'''
    def copy_folder(self):
        global buff
        buff = [self.path_name]  # Заносим в буфер путь к копируемым объектам
        views.update_ful()

    '''перемещение файла'''
    def move_file_folder(self):
        global flag
        flag = True  # устанавливаем флаг на перемещение (для удаления после копирования)
        self.copy_folder()  # Вызываем копирование

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
        views.update_ful()

