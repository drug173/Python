"""
Модуль считывает показатели загрузки
центрального процессора
и оперативной памяти.
"""

import psutil as pt


class Info_cpu():
    """Использование процессора и оперативной памяти."""

    def __init__(self):
        """Количество физических и логических ядер процессора."""
        self.cpu_count = pt.cpu_count(logical=False)
        self.cpu_count_logical = pt.cpu_count()

    def cpu_percent_return(self):
        """Считывает нагрузку на ядра процессора."""
        return pt.cpu_percent(percpu=True)

    def cpu_one_return(self):
        """Считывает общую загрузку процессора."""
        return pt.cpu_percent()

    def ram_usage(self):
        """Считывает загрузку оперативной памяти."""
        return pt.virtual_memory()
