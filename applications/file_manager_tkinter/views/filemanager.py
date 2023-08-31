
from tkinter import ttk
import tkinter as tk
from views.views import FileManager


class FileManagerList_2(FileManager):
    ''' Класс основного окна, наследующий FileManager'''

    def __init__(self, window, frame):
        super().__init__(window, frame)
        self.window = window
        self.load_drive_options()
        self.load_file_system()

    def load_drive_options(self):
        drive_list = self.get_drives()
        for drive in drive_list:
            drive_option = tk.Button(self.canvas, text=drive, command=lambda d=drive: self.change_drive(d))
            drive_option.pack(side=tk.LEFT)

    '''функция нажатия кнопки смены привода'''

    def change_drive(self, drive):
        self.drive_letter = drive[0]
        self.current_path = drive
        # self.path_label.config(text=self.current_path)
        self.path_text.set(self.current_path)
        self.update_file_system()


class FileManagerList(FileManager):
    ''' Класс основного окна, наследующий FileManager'''

    def __init__(self, window, frame):
        super().__init__(window, frame)
        self.window = window
        self.load_drive_options()
        self.load_file_system()

    ''' загрузка кнопок приводов'''

    def load_drive_options(self):
        drive_list = self.get_drives()
        for drive in drive_list:
            drive_option = tk.Button(self.canvas, text=drive, command=lambda d=drive: self.change_drive(d))
            drive_option.pack(side=tk.LEFT)

    '''функция нажатия кнопки смены привода'''

    def change_drive(self, drive):
        self.drive_letter = drive[0]
        self.current_path = drive
        #self.path_label.config(text=self.current_path)
        self.path_text.set(self.current_path)
        self.update_file_system()
