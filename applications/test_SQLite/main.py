import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from memory_profiler import profile, memory_usage  #  для вывода информации об используемой памяти


# Задайте имя базы данных SQLite
db_filename = 'cheaters.db'

# Функция загрузки памяти
def measure_memory_usage():
    usage = resource.getrusage(resource.RUSAGE_SELF)
    return usage.ru_maxrss  # Возвращаем максимальное потребление памяти в килобайтах


""" ЗАДАЧА 1: Создание таблицы в SQLite """
def create_table():
    conn = sqlite3.connect(db_filename)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cheaters_data (
            timestamp DATETIME,
            player_id INTEGER,
            event_id INTEGER,
            error_id INTEGER,
            json_server TEXT,
            json_client TEXT
        )
    ''')

    conn.commit()
    conn.close()


""" ЗАДАЧА 2: Функция для обработки данных """
# Функция для получения списка player_id из таблицы cheaters с баном, предыдущими сутками или раньше
def cheaters_with_ban_before(conn, previous_day):
    """
        Из таблицы  cheaters  базы данных получает список.

           Args:
               conn: соединение с базой данных
			   previous_day (datetime): дата до которого ищем
    """
    cursor = conn.cursor()
    cursor.execute('''
        SELECT player_id FROM cheaters
        WHERE ban_time < ?
    ''', (previous_day,))
    result = cursor.fetchall()
    return [row[0] for row in result]

@profile  #  узнать загрузку памяти вывод в консоль
def process_data(date):
    """
       Обрабатывает данные из файлов client.csv и server.csv.

       Args:
           date (datetime): Дата, для которой нужно обработать данные.
       """
    # Подключение к базе данных SQLite
    conn = sqlite3.connect(db_filename)
    cursor = conn.cursor()

    # 1) Выгрузить данные из client.csv и server.csv
    client_data = pd.read_csv('client.csv')
    server_data = pd.read_csv('server.csv')

    # Преобразовать числовой Unix timestamp в объекты datetime
    client_data['timestamp'] = pd.to_datetime(client_data['timestamp'], unit='s')
    server_data['timestamp'] = pd.to_datetime(server_data['timestamp'], unit='s')

    # Фильтровать данные по выбранной дате
    client_data = client_data[client_data['timestamp'].dt.date == date.date()]
    server_data = server_data[server_data['timestamp'].dt.date == date.date()]

    # 2) Объединить данные по error_id
    merged_data = pd.merge(client_data, server_data, on='error_id', how='inner')

    # 3) Исключить записи с player_id, которые есть в таблице cheaters
    #     с баном, предыдущими сутками или раньше относительно timestamp из server.scv
    merged_data = merged_data[~merged_data['player_id'].isin(cheaters_with_ban_before(conn, date))]
    # Преобразуем дату в удобочитаемый вид для записи в базу
    merged_data['timestamp_x'] = merged_data['timestamp_x'].dt.strftime('%Y-%m-%d %H:%M:%S')
    # 4) Выгрузить данные в таблицу cheaters_data
    merged_data[['timestamp_x', 'player_id', 'event_id', 'error_id', 'description_x', 'description_y']].to_sql(
        'cheaters_data', conn, if_exists='replace', index=False)

    column_mapping = {
        'timestamp_x': 'timestamp',
        'player_id': 'player_id',
        'event_id_x': 'event_id',
        'error_id_x': 'error_id',
        'description_x': 'json_server',
        'description_y': 'json_client'
    }
    column_order = ['timestamp', 'player_id', 'event_id', 'error_id', 'json_server', 'json_client']

    merged_data.rename(columns=column_mapping)[column_order].to_sql('cheaters_data', conn, if_exists='replace',
                                                                    index=False)

    conn.commit()  # Сохранить изменения в базе данных
    conn.close()

    """ЗАДАЧА 3: вычисление потребления памяти """
    mem_usage = memory_usage()
    print(f"Потребление памяти: {mem_usage} MB")  # Выводим информацию об потреблении памяти


if __name__ == "__main__":
    create_table()  # создаём таблицу  (Задание 1)
    selected_date = '2021-05-25'  # Замените на желаемую дату
    selected_date = datetime.strptime(selected_date, '%Y-%m-%d')  # Преобразовать переменную date в объект datetime
    process_data(selected_date)   # Записываем данные в таблицу  (Задание 2 и Задание 3)
