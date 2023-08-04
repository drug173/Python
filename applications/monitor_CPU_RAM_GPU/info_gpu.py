import pynvml
from pynvml import nvmlInit, nvmlDeviceGetCount, nvmlDeviceGetHandleByIndex, nvmlDeviceGetUtilizationRates, nvmlDeviceGetMemoryInfo, NVMLError_LibraryNotFound

global_gpu = 0.0

class Info_gpu:
    def __init__(self):
        try:
            nvmlInit()
            self.handle = nvmlDeviceGetHandleByIndex(0)  # Assuming one GPU is present
            self.device_count = nvmlDeviceGetCount()
        except NVMLError_LibraryNotFound:
            print("Библиотека pynvml не найдена. Проверьте установку и наличие видеокарты NVIDIA.")
            # Дополнительные действия, если библиотека pynvml не найдена или отсутствует видеокарта
            self.handle = None
            self.device_count = 0

    def __del__(self):
        if self.device_count > 0:
            pynvml.nvmlShutdown()

    def get_handle(self, i):
        if self.device_count > 0:
            handle = nvmlDeviceGetHandleByIndex(i)
            return handle
        else:
            return 0

    def gpu_utilization(self, handle):
        if self.device_count > 0:
            utilization = nvmlDeviceGetUtilizationRates(handle)
            return utilization
        else:
            return 0

    def gpu_video_memory_info(self, handle):
        if self.device_count > 0:
            mem_info = nvmlDeviceGetMemoryInfo(handle)
            return mem_info
        else:
            return 0


