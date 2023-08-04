import tkinter as tk
from tkinter import ttk, BOTH
import sys
from info_cpu import Info_cpu

from info_gpu import Info_gpu, global_gpu
from update_widget import Configure_widgets

#from style import style2, style1


"""Создает графический интерфейс."""
class Application(tk.Tk, Configure_widgets):
    """Создаёт окно."""
    def __init__(self):
        tk.Tk.__init__(self)
        self.label1 = None
        self.combo_win = None
        self.bar1 = None
        self.bar2 = None
        self.bar3 = None
        self.bar4 = None

        self.ram_bar = None
        self.gpu_pbar = None
        self.wheel = None
        self.bar_one = None



        self.title('Мониторинг')
        self.attributes('-alpha', 0.9)
        self.attributes('-topmost', False)
        self.overrideredirect(False)
        self.resizable(True, True)
        self.geometry("250x800")
        self.minsize(200, 100)
        self.maxsize(600, 1000)

        self.gpu = Info_gpu()
        self.cpu = Info_cpu()
        self.run_set_ui()








    def run_set_ui(self):
        """Старт создания виджета."""
        self.set_ui()

        self.bar1 = ttk.LabelFrame(self, text='ИНДИКАТОРЫ GPU')
        self.bar1.pack(fill=tk.BOTH)

        self.gpu_pbar_var = tk.DoubleVar()  # Переменная для связи с прогрессбаром gpu_pbar
        self.video_memory_pbar_var = tk.DoubleVar()  # Переменная для связи с прогрессбаром video_memory_pbar

        self.make_bar_gpu()

        self.bar3 = ttk.LabelFrame(self, text='ИНДИКАТОРЫ CPU')
        self.bar3.pack(fill=tk.BOTH)

        self.bar4 = ttk.LabelFrame(self, text='ИНДИКАТОРЫ RAM')
        self.bar4.pack(fill=tk.BOTH)

        self.make_bar_cpu()
        self.configure_widgets()


    def set_ui(self):

        self.bar2 = ttk.Frame(self)
        self.bar2.pack(fill=tk.X)

        self.combo_win = ttk.Combobox(self.bar2,
                                      values=["Всё", "Мин"],
                                      width=11, state='readonly')
        self.combo_win.current(0)
        self.combo_win.pack(side=tk.LEFT)
        ttk.Button(self.bar2, text='О программе', command=self.make_info_win).pack(side=tk.LEFT)  # вкладка информации о программе

        self.combo_win.bind('<<ComboboxSelected>>', self.choise_combo)  # Список выбора отображения окна

    def make_bar_cpu(self):
        """Создание индикаторов выполнения и меток, указывающих на загрузку процессора и оперативной памяти."""
        ttk.Label(self.bar3, text=f'Ядер: {self.cpu.cpu_count}, потоков: {self.cpu.cpu_count_logical}', anchor=tk.W, padding=(10, 0, 0, 0)).pack(fill=tk.X)
        style3 = ttk.Style(self)
        style3.layout("LabeledProgressbarRam",
                  [('LabeledProgressbarRam.trough',
                    {'children': [('LabeledProgressbarRam.pbar',
                                   {'side': 'left', 'sticky': 'ns'}),
                                  ("LabeledProgressbarRam.label",  #
                                   {"sticky": ""})],
                     'sticky': 'nswe'})])
        self.list_label = []
        self.list_pbar = []

        for i in range(self.cpu.cpu_count_logical):
            self.list_label.append(ttk.Label(self.bar3, anchor=tk.W, padding=(10, 0, 0, 0)))
            self.list_pbar.append(ttk.Progressbar(self.bar3, length=230))
        for i in range(self.cpu.cpu_count_logical):
            self.list_label[i].pack(fill=tk.X)
            self.list_pbar[i].pack(fill=tk.X)

        self.ram_lab = ttk.Label(self.bar4, text='', anchor=tk.W, padding=(10, 0, 0, 0))
        self.ram_lab.pack(fill=tk.X)
        self.ram_bar = ttk.Progressbar(self.bar4, length=150, style="LabeledProgressbarRam")
        style3.configure("LabeledProgressbarRam", text=f"{0.0}%", background="navy")
        self.ram_bar.pack(fill=tk.X, side=tk.LEFT, expand=1)

    def make_bar_gpu(self):
        style1 = ttk.Style()
        # Определение стиля для прогрессбара
        style1.layout("CustomHorizontal.TProgressbar",
                      [('CustomHorizontal.Progressbar.trough',
                        {'children': [('CustomHorizontal.Progressbar.pbar',
                                       {'side': 'left', 'sticky': 'ns'})],
                         'sticky': 'nswe'}),
                       ('CustomHorizontal.Progressbar.label', {'sticky': ''})])

        style1.configure("CustomHorizontal.TProgressbar",
                         thickness=15,
                         troughcolor='#E0E0E0',
                         bordercolor='#E0E0E0',
                         lightcolor='#E0E0E0',
                         darkcolor='#E0E0E0',
                         background='#C5E1A5',
                         troughrelief='flat')

        style2 = ttk.Style()
        # Определение стиля для прогрессбара
        style2.layout("CustomHorizontal.TProgressbar1",
                      [('CustomHorizontal.Progressbar.trough',
                        {'children': [('CustomHorizontal.Progressbar.pbar',
                                       {'side': 'left', 'sticky': 'ns'})],
                         'sticky': 'nswe'}),
                       ('CustomHorizontal.Progressbar.label', {'sticky': ''})])

        style2.configure("CustomHorizontal.TProgressbar",
                         thickness=15,
                         troughcolor='#E0E0E0',
                         bordercolor='#E0E0E0',
                         lightcolor='#E0E0E0',
                         darkcolor='#E0E0E0',
                         background='#C5E1A5',
                         troughrelief='flat')

        # Создание виджетов с определенным стилем
        # Загрузка GPU
        self.gpu_label = ttk.Label(self.bar1, text='Загрузка GPU:', anchor=tk.W, padding=(10, 0, 0, 0))
        self.gpu_label.pack(fill=tk.X)
        # ПРОГРЕССБАР загрузки GPU
        self.gpu_pbar = ttk.Progressbar(self.bar1, length=230, mode='determinate',
                                        style="CustomHorizontal.TProgressbar1")
        self.gpu_pbar.pack(fill=tk.X)
        # ВСЕГО ПАМЯТИ GPU
        self.total_video_memory_label = ttk.Label(self.bar1, text='Всего видео памяти:', anchor=tk.W,
                                                  padding=(10, 0, 0, 0))
        self.total_video_memory_label.pack(fill=tk.X)
        # Занято памяти GPU
        self.used_video_memory_label = ttk.Label(self.bar1, text='Загрузка памяти:', anchor=tk.W, padding=(10, 0, 0, 0))
        self.used_video_memory_label.pack(fill=tk.X)
        # ПРОГРЕССБАР загрузки GPU
        self.video_memory_pbar = ttk.Progressbar(self.bar1, length=230, mode='determinate',
                                                 style="CustomHorizontal.TProgressbar")
        self.video_memory_pbar.pack(fill=tk.X)
        # Настройка стиля прогрессбара
        style1.configure("CustomHorizontal.TProgressbar", text=f"{self.gpu_pbar_var.get()}", font=("Arial", 10, "bold"))
        style2.configure("CustomHorizontal.TProgressbar1", text=f"{global_gpu}%", font=("Arial", 10, "bold"),
                         background="BLUE")

    def configure_widgets(self):

        configure = Configure_widgets(self, self.gpu, self.video_memory_pbar, self.gpu_pbar, self.used_video_memory_label, self.total_video_memory_label, self.gpu_label, self.cpu, self.bar_one, self.list_label, self.list_pbar, self.ram_lab, self.ram_bar)  # Передача объекта Info_gpu и виджета video_memory_pbar
        configure.update_progressbar()

    def configure_widgets2(self):

        configure = Configure_widgets(self, self.gpu, self.video_memory_pbar, self.gpu_pbar, self.used_video_memory_label, self.total_video_memory_label, self.gpu_label, self.cpu, self.bar_one, self.list_label, self.list_pbar, self.ram_lab, self.ram_bar)  # Передача объекта Info_gpu и виджета video_memory_pbar
        configure.update_minimal_progressbar()

    # вкладка информации о программе
    def make_info_win(self):
        info_win = tk.Toplevel(self)
        info_win.title("О программе")
        info_win.geometry("330x150")
        info_win.resizable(False, False)
        info_win.bar = ttk.Frame(info_win)
        info_win.bar.pack(fill=tk.X)
        ttk.Button(info_win.bar, text='<< Назад', command=info_win.destroy).pack(side=tk.LEFT)
        info_win.bar2 = ttk.LabelFrame(info_win, text='   Программа мониторинг ресурсов')
        info_win.bar2.pack(fill=tk.X)
        info_win.lab1 = ttk.Label(info_win.bar2, text='     \
                                \n   Программа реализована на Python 3, с применением \
                                \n   библиотек tkinter, psutill и pynvml.\
                                \n \
                                \n              Накодил  Лейман М.А.\
                                \n              почта: makc.mon@mail.ru \
                                \n                     ').pack(fill=tk.X, side=tk.LEFT)


        info_win.update()
        info_win.grab_set()

        if self.wheel is not None:
            self.after_cancel(self.wheel)
            self.wheel = None
        info_win.protocol("WM_DELETE_WINDOW", info_win.destroy)


    # Список выбора отображения окна
    def choise_combo(self, event):
        """
        Выбранное событие в выпадающем списке.
        Прерывание цикла обновления виджетов.
        Развязывание событий, удаление виджетов.
        Создание виджетов небольших окон.
        """
        if self.combo_win.current() == 1:
            self.combo_win.unbind('<<ComboboxSelected>>')
            if self.wheel is not None:
                self.after_cancel(self.wheel)
                self.wheel = None
            self.clear_win()
            self.update()
            self.run_set_ui_min()
        else:
            self.combo_win.unbind('<<ComboboxSelected>>')
            if self.wheel is not None:
                self.after_cancel(self.wheel)
                self.wheel = None
            self.clear_win()
            self.update()
            self.make_full_win() # Возврат к основному окну



    def run_set_ui_min(self):
        """старт создания виджетов в минимальном окне"""

        self.geometry("250x200")

        self.gpu_pbar_var = tk.DoubleVar()  # Переменная для связи с прогрессбаром gpu_pbar
        self.video_memory_pbar_var = tk.DoubleVar()  # Переменная для связи с прогрессбаром video_memory_pbar
        self.cpu_pbar_var = tk.DoubleVar()
        self.ram_pbar_var = tk.DoubleVar()

        self.bar2 = ttk.Frame(self)
        self.bar2.pack(fill=tk.X)
        self.combo_win = ttk.Combobox(self.bar2,
                                      values=["Всё", "Мин"],
                                      width=9, state='readonly')
        self.combo_win.bind('<<ComboboxSelected>>', self.choise_combo)
        self.combo_win.current(1)
        self.combo_win.pack(side=tk.LEFT)

        self.bar3 = ttk.LabelFrame(self, text='ИНДИКАТОРЫ CPU')
        self.bar3.pack(fill=tk.BOTH)
        self.bar4 = ttk.LabelFrame(self, text='ИНДИКАТОРЫ RAM')
        self.bar4.pack(fill=tk.BOTH)
        self.bar1 = ttk.LabelFrame(self, text='ИНДИКАТОРЫ GPU')
        self.bar1.pack(fill=tk.BOTH)

        self.make_minimal_win()  # Separate method to create minimal window widgets
        self.configure_widgets2()

        # переход к окну  с минимальным отображением
    def make_minimal_win(self):
        """Создание виджетов в минимальном окне."""
        s1 = s = ttk.Style()

        ##############
        # добавим стиль прогресс бара для отображения надписи
        s.layout("Label_CPU",
                 [('Label_CPU.trough',
                   {'children': [('Label_CPU.pbar',
                                  {'side': 'left', 'sticky': 'ns'}),
                                 ("Label_CPU.label",
                                  {"sticky": ""})],
                    'sticky': 'nswe'})])
        ###################
        s1.layout("Labele_Ram",
                  [('Labele_Ram.trough',
                    {'children': [('Labele_Ram.pbar',
                                   {'side': 'left', 'sticky': 'ns'}),
                                  ("Labele_Ram.label",  #
                                   {"sticky": ""})],
                     'sticky': 'nswe'})])
        ####################

        s4 = ttk.Style()
        # Определение стиля для прогрессбара
        s4.layout("Label_Ram_GPU",
                      [('Label_Ram_GPU.trough',
                        {'children': [('Label_Ram_GPU.pbar',
                                       {'side': 'left', 'sticky': 'ns'})],
                         'sticky': 'nswe'}),
                       ('Label_Ram_GPU.label', {'sticky': ''})])

        s4.configure("Label_Ram_GPU",
                         thickness=15,
                         troughcolor='#E0E0E0',
                         bordercolor='#E0E0E0',
                         lightcolor='#E0E0E0',
                         darkcolor='#E0E0E0',
                         background='#C5E1A5',
                         troughrelief='flat')

        s3 = ttk.Style()
        # Определение стиля для прогрессбара
        s3.layout("Label_GPU",
                      [('Label_GPU.trough',
                        {'children': [('Label_GPU.pbar',
                                       {'side': 'left', 'sticky': 'ns'})],
                         'sticky': 'nswe'}),
                       ('Label_GPU.label', {'sticky': ''})])

        s3.configure("Label_GPU",
                         thickness=15,
                         troughcolor='#E0E0E0',
                         bordercolor='#E0E0E0',
                         lightcolor='#E0E0E0',
                         darkcolor='#E0E0E0',
                         background='#C5E1A5',
                         troughrelief='flat')

        self.bar_one = ttk.Progressbar(self.bar3, length=150,mode='determinate', style="Label_CPU")
        self.bar_one.pack(fill=tk.X, side=tk.LEFT, expand=1)
        s.configure("Label_CPU", text="Процессор   ", background="GREEN")

        self.ram_bar = ttk.Progressbar(self.bar4, length=150,mode='determinate', style="Labele_Ram")
        self.ram_bar.pack(fill=tk.X, side=tk.LEFT, expand=1)
        s1.configure("Labele_Ram", text="Память   ", background="navy")

        self.gpu_pbar = ttk.Progressbar(self.bar1, length=150, mode='determinate', style="Label_GPU")
        self.gpu_pbar.pack(fill=tk.X, expand=1)

        self.label1 = ttk.Label(self.bar1, text='', anchor=tk.W, padding=(10, 0, 0, 0))
        self.label1.pack(fill=tk.X)

        self.video_memory_pbar = ttk.Progressbar(self.bar1, length=230, mode='determinate', style="Label_Ram_GPU")
        self.video_memory_pbar.pack(fill=tk.X)

        s3.configure("Label_GPU", text=f"GPU: {global_gpu}%", font=("Arial", 10, "bold"), background="GREEN")

        s4.configure("Label_Ram_GPU", text=f"Память  GPU: {global_gpu}%", font=("Arial", 10, "bold"), background="BLUE")

    # Возврат к основному окну
    def make_full_win(self):
        """
         Прерывание цикла обновления виджетов.
        Удаление виджетов небольших окон.
        Обновление основного графического интерфейса.
        """
        self.geometry("250x800")

        #self.clear_win()
        self.update()
        self.run_set_ui()

        self.combo_win.current(0)
















