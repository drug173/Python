

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
            self.label4 = tk.Label(self, text=self.name_action_2 + " в:    " + path_name_in)
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



