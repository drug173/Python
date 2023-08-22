# -*- coding: utf-8 -*-
"""
Created on Thu Jul  6 11:15:42 2023

@author: drug1
"""
import views
from views import FileManagerList, FileManagerList_2
from views import Applications
import tkinter as tk
from PIL import Image, ImageTk
import os
import psutil
import pyautogui
import time
from tkinter import ttk
import asyncio

def exit_app():
    if root:
        root.destroy()

def main():
    global root
    root = tk.Tk()
    root.title("Файловый  менеджер")
    root.iconbitmap("ico1.ico")
    root.configure(background="lightgray")
    # root.state('zoomed')
    root.geometry("1000x800")
    root.update()
    len_1 = root.winfo_width()
    print(len_1, "len")
    root.protocol("WM_DELETE_WINDOW", exit_app)
    #views.flag = True
    applications = Applications(root)
    applications.check_var.set(True)  # Скрываем скрытые файлы и папки
    root.mainloop()


if __name__ == "__main__":
    main()
