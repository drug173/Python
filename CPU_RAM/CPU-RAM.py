"""Главный файл."""

import tkinter as tk
from tkinter import ttk, BOTH
import sys
from process import CpuBar
from widget_update import Configure_widjets


class Application(tk.Tk, Configure_widjets):
    """Создает графический интерфейс."""

    def __init__(self):
        """Сосдаёт окно."""
        tk.Tk.__init__(self)
        self.lab1 = None
        self.bar = None
        self.attributes('-alpha', 0.9)
        self.attributes('-topmost', False)
        self.overrideredirect(False)
        self.resizable(True, False)
        self.title('Монитор')

        self.cpu = CpuBar()
        self.run_set_ui()

    def run_set_ui(self):
        """Старт создания виджета."""
        self.set_ui()
        self.make_bar_cpu_usage()
        self.configure_cpu_bar()

    def set_ui(self):
        # notebook = ttk.Notebook()
        # notebook.pack(expand=True, fill=BOTH)
        # frame1 = ttk.Frame(notebook)
        # frame2 = ttk.Frame(notebook)
        #
        # frame1.pack(fill=BOTH, expand=True)
        # frame2.pack(fill=BOTH, expand=True)
        # notebook.add(frame1, text="Python")
        # notebook.add(frame2, text="О программе")

        self.bar2 = ttk.Frame(self)
        self.bar2.pack(fill=tk.X)

        self.combo_win = ttk.Combobox(self.bar2,
                                      values=["Всё", "Мин"],
                                      width=11, state='readonly')

        self.combo_win.current(0)
        self.combo_win.pack(side=tk.LEFT)
        ttk.Button(self.bar2, text='О программе', command=self.make_info_win).pack(side=tk.LEFT)


        self.bar = ttk.LabelFrame(self, text='Индикаторы загрузки')
        self.bar.pack(fill=tk.BOTH)

        # self.bind_class('Tk', '<Enter>', self.enter_mouse)
        # self.bind_class('Tk', '<Leave>', self.leave_mouse)
        self.combo_win.bind('<<ComboboxSelected>>', self.choise_combo)

    def make_bar_cpu_usage(self):
        """Создание индикаторов выполнения и меток, указывающих на загрузку процессора и оперативной памяти."""
        ttk.Label(self.bar,
                  text=f'ядер: {self.cpu.cpu_count}, потоков: {self.cpu.cpu_count_logical}',
                  anchor=tk.CENTER).pack(fill=tk.X)

        self.list_label = []
        self.list_pbar = []

        for i in range(self.cpu.cpu_count_logical):
            self.list_label.append(ttk.Label(self.bar, anchor=tk.CENTER))
            self.list_pbar.append(ttk.Progressbar(self.bar, length=230))
        for i in range(self.cpu.cpu_count_logical):
            self.list_label[i].pack(fill=tk.X)
            self.list_pbar[i].pack(fill=tk.X)

        self.ram_lab = ttk.Label(self.bar, text='', anchor=tk.CENTER)
        self.ram_lab.pack(fill=tk.X)
        self.ram_bar = ttk.Progressbar(self.bar, length=230)
        self.ram_bar.pack(fill=tk.X)

    def make_minimal_win(self):
        """Создание виджетов в минимальном окне."""

        self.bar2 = ttk.Frame(self)
        self.bar3 = ttk.Frame(self)
        self.bar2.pack(fill=tk.X)
        self.bar3.pack(fill=tk.X)



        self.combo_win = ttk.Combobox(self.bar2,
                                      values=["Всё", "Мин"],
                                      width=9, state='readonly')
        self.combo_win.bind('<<ComboboxSelected>>', self.choise_combo)
        self.combo_win.current(1)
        self.combo_win.pack(side=tk.LEFT)

        ##############
        s1 = s = ttk.Style(self)
        # добавим стиль прогресс бара для отображения надписи
        s.layout("LabeledProgressbar",
                 [('LabeledProgressbar.trough',
                   {'children': [('LabeledProgressbar.pbar',
                                  {'side': 'left', 'sticky': 'ns'}),
                                 ("LabeledProgressbar.label",
                                  {"sticky": ""})],
                    'sticky': 'nswe'})])
        ###################
        s1.layout("LabeledProgressbarRam",
                 [('LabeledProgressbarRam.trough',
                   {'children': [('LabeledProgressbarRam.pbar',
                                  {'side': 'left', 'sticky': 'ns'}),
                                 ("LabeledProgressbarRam.label",  #
                                  {"sticky": ""})],
                    'sticky': 'nswe'})])
        ####################

        self.bar_one = ttk.Progressbar(self.bar3, length=150, style="LabeledProgressbar")
        self.bar_one.pack(fill=tk.X, side=tk.LEFT, expand=1)
        s.configure("LabeledProgressbar", text="Процессор   ", background="BLUE")
        self.ram_bar = ttk.Progressbar(self.bar3, length=150, style="LabeledProgressbarRam")
        s1.configure("LabeledProgressbarRam", text="Память   ", background="GREEN")
        self.ram_bar.pack(fill=tk.X, side=tk.LEFT, expand=1)

        self.update()
        self.configure_minimal_win()

    def choise_combo(self, event):
        """
        Выбранное событие в выпадающем списке.
        Прерывание цикла обновления виджетов.
        Развязывание событий, удаление виджетов.
        Создание виджетов небольших окон.
        """
        if self.combo_win.current() == 1:
            self.combo_win.unbind('<<ComboboxSelected>>')
            self.after_cancel(self.wheel)
            self.clear_win()
            self.update()
            self.make_minimal_win()
        else:
            self.combo_win.unbind('<<ComboboxSelected>>')
            self.after_cancel(self.wheel)
            self.clear_win()
            self.update()
            self.make_full_win()

    def make_full_win(self):
        """
         Прерывание цикла обновления виджетов.
        Удаление виджетов небольших окон.
        Обновление основного графического интерфейса.
        """
        self.after_cancel(self.wheel)
        self.clear_win()
        self.update()
        self.run_set_ui()
        # self.enter_mouse('')
        self.combo_win.current(0)

    def make_info_win(self):
        self.after_cancel(self.wheel)
        self.clear_win()
        self.bar = ttk.Frame(self)
        self.bar.pack(fill=tk.X)
        ttk.Button(self.bar, text='<< Назад', command=self.make_full_win).pack(side=tk.LEFT)
        self.bar2 = ttk.LabelFrame(self, text='   Программа мониторинг ресурсов')
        self.bar2.pack(fill=tk.X)
        self.lab1 = ttk.Label(self.bar2, text='     \
                                \n   Программа nреализована на Python 3, с применением \
                                \n   библиотек tkinter и psutill\
                                \n \
                                \n              Накодил  Лейман М.А.\
                                \n              почта: makc.mon@mail.ru').pack(fill=tk.X, side=tk.LEFT)
        self.update()


if __name__ == '__main__':
    root = Application()
    root.mainloop()
