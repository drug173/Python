
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
from views.filemanager import FileManagerList, FileManagerList_2


# file_manager2 = None
# file_manager3 = None
check_operating_var = None

class Applications:
    def __init__(self, root, event=None):
        self.label = None  # Атрибут для хранения ссылки на виджет Label
        self.resized = False
        self.root = root  # ССылка на окно
        menu_bar = tk.Menu(self.root)

        self.len_1 = self.root.winfo_width()
        self.root.config(menu=menu_bar)
        file_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="МЕНЮ", menu=file_menu)

        file_menu.add_command(label="Выход", command=self.root.quit)
        file_menu.add_separator()
        # global check_hidden_var
        # global check_operating_var
        self.check_hidden_var = tk.BooleanVar()   # Переменная скрываем ли скрытые папки
        self.check_operating_var = tk.BooleanVar()   # Переменная быстрое или медленное копирование (удаление)
        file_menu.add_checkbutton(label="Отображать скрытые объекты", variable=self.check_hidden_var, command=self.hidden_var_callback)
        file_menu.add_checkbutton(label="Быстрые операции с файлами", variable=self.check_operating_var, command=self.operating_var_callback)


        notebook = ttk.Notebook(self.root)
        notebook.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.tab1 = tk.Frame(notebook)
        self.tab2 = tk.Frame(notebook)
        self.tab3 = tk.Frame(notebook)
        notebook.add(self.tab1, text="Проводник")
        notebook.add(self.tab2, text="Вкладка")
        notebook.add(self.tab3, text="О программе")


        canvas2 = tk.Canvas(self.tab1, bg="#A9A9A9")
        canvas2.pack(side=tk.LEFT, padx=2, fill=tk.BOTH, expand=True)

        canvas3 = tk.Canvas(self.tab1, bg="#A9A9A9")
        canvas3.pack(side=tk.LEFT, padx=1, fill=tk.BOTH, expand=True)


        self.file_manager2 = FileManagerList_2(self, canvas2)
        self.file_manager3 = FileManagerList(self, canvas3)
        root.bind("<Configure>", self.event_resize)
        self.set_text(self.len_1)
        self.root.update()
        self.check_operating_var.trace("w", self.operating_var_callback)
        self.check_hidden_var.trace("w", self.hidden_var_callback)

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
        self.label3= ttk.Label(self.tab3, text="Менеджер позволяет: копировать, удалять, переносить файлы.", font=("Arial", 14), anchor='w', wraplength=len_1-120)
        self.label4 = ttk.Label(self.tab3, text="Множественное выделение: Shift либо Ctrl+клик мышкой ", font=("Arial", 14), anchor='w', wraplength=len_1-120)

        self.label1 = ttk.Label(self.tab3, text="  Разработка:   Лейман М.А.", font=("Arial", 12), anchor='w')
        self.label2 = ttk.Label(self.tab3, text="  email:  leiman@sfedu.ru.", font=("Arial", 12), anchor='w')

        self.label.pack(fill=tk.X, padx=40)
        self.label3.pack(fill=tk.X, padx=20, pady=10)
        self.label4.pack(fill=tk.X, padx=20)

        self.label2.pack(fill=tk.X, padx=40, pady=7, side=tk.BOTTOM)
        self.label1.pack(fill=tk.X, padx=40, pady=2, side=tk.BOTTOM)
        self.label.image = logo  # Сохраняем ссылку на объект PhotoImage


    def operating_var_callback(self, *args):
        global check_operating_var
        check_operating_var = self.check_operating_var.get()

    def hidden_var_callback(self, *args):
        global check_hidden_var
        check_hidden_var = self.check_hidden_var.get()
        if check_hidden_var:
            self.root.title("Файловый  менеджер  (скрытые объекты отображаются)")
        else:
            self.root.title("Файловый  менеджер  (скрытые объекты скрываются)")