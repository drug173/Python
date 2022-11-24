
"""Модуль настраивает и обновляет графический интерфейс """
from tkinter import ttk

class Configure_widjets:
    """
   Класс настраивает и обновляет графический интерфейс
    """

    def __init__(self):
        self.bar_one = None
        self.ram_bar = None
        self.ram_lab = None
        self.list_pbar = None
        self.list_label = None
        self.cpu = None

    def configure_cpu_bar(self):
        """
        Обновление виджетов загрузки процессора и оперативной
        памяти главного окна.
        """
        r = self.cpu.cpu_percent_return()
        for i in range(self.cpu.cpu_count_logical):
            self.list_label[i].configure(text=f'поток {i + 1} - загрузка: {r[i]}%')
            self.list_pbar[i].configure(value=r[i])

        r2 = self.cpu.ram_usage()
        self.ram_lab.configure(text=f'RAM всего: {round(r2[0] / 1048576)} Мб,\
                 \n загрузка: {r2[2]}%,\
                 \n используется: {round(r2[3] / 1048576)} Мб,\
                 \n свободно: {round(r2[1] / 1048576)} Мб')
        self.ram_bar.configure(value=r2[2])
        self.wheel = self.after(750, self.configure_cpu_bar)



    def clear_win(self):
        """Удаление виджетов."""
        for i in self.winfo_children():
            i.destroy()

    def configure_minimal_win(self):
        """Обновление виджетов загрузки процессора и
             оперативной памяти в минимальном окне."""

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
                                  ("LabeledProgressbarRam.label",
                                   {"sticky": ""}),
                                  ("LabeledProgressbarRam.text",
                                   {"sticky": ""})
                                  ],
                     'sticky': 'nswe'})])
        ####################

        r3 = self.cpu.cpu_one_return()
        self.bar_one.configure(value=r3)

        r4 = self.cpu.ram_usage()[2]

        # self.ram_bar = ttk.Progressbar(self, length=150, style="LabeledProgressbarRam")
        # s1.configure("LabeledProgressbarRam", value=r4, text=r4, background="GREEN")
        self.ram_bar.configure(value=r4)
        self.wheel = self.after(750, self.configure_minimal_win)
