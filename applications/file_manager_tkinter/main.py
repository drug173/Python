# -*- coding: utf-8 -*-
"""
Created on Thu Jul  6 11:15:42 2023

@author: drug1
"""
import views
#from views.views import FileManagerList, FileManagerList_2
from views.aplication import Applications

import tkinter as tk
from PIL import Image, ImageTk
import os
import psutil
import pyautogui
import time
from tkinter import ttk
import asyncio

def exit_app():   # Выход из приложения при закрытии
    if root:
        root.destroy()

def main():
    global root
    root = tk.Tk()   # Создание главного окна
    root.title("Файловый  менеджер")  # Заголовок окна
    root.iconbitmap("ico1.ico")
    root.configure(background="lightgray")
    #root.state('zoomed')
    root.geometry("1000x800")
    #root.update()
    root.protocol("WM_DELETE_WINDOW", exit_app)   # обработка нажатия на закрытие окна


    applications = Applications(root)   # Создаём фреймы и заполняем виджетами
    applications.check_hidden_var.set(True)  # Скрываем скрытые файлы и папки
    applications.check_operating_var.set(True)  # Разные подходы к операциям (копирование, удаление)
    root.mainloop()  # Запуск обработчика цикла событий


if __name__ == "__main__":
    main()
