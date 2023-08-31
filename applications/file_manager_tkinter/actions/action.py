
import os


"""Объём выделенных элементов"""

def get_selected_size(current_path, selected_path):
    total_size = 0
    for item_path1 in selected_path:
        item_path = os.path.join(current_path, item_path1)
        if os.path.isdir(item_path):
            item_path = os.path.join(current_path, item_path1)
            total_size = total_size + get_folder_size(item_path)
        else:
            item_path = os.path.join(current_path, item_path1)
            total_size = total_size + os.path.getsize(item_path)

    return total_size


"""Объём папки"""

def get_folder_size(folder_path):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(folder_path):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            total_size += os.path.getsize(file_path)
    return total_size


"""Конвертирование Байт"""

def get_size(byte_size):
    sizes = [" Б", " КБ", " МБ", " ГБ", " ТБ"]
    i = 0
    while byte_size >= 1024 and i < len(sizes) - 1:
        byte_size /= 1024.0
        i += 1
    return str(round(byte_size, 2)) + sizes[i]



