#
#  Второй способ с selenium
#  С использованием "CHROMEDRIVER"
# С выбором дат начала и конца предыдущего месяца

import xlwings as xw
from decimal import Decimal
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from datetime import datetime, timedelta
from selenium.webdriver.common.keys import Keys
import pyperclip
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options


#  Открытие веб страницы
def opening_web_page(url, driver_1):
    XPath_calendar_1 = '//*[@id="fromDate"]'
    XPath_calendar_2 = '//*[@id="tillDate"]'
    class_name_show_button = "ui-button__label"

    #  Получаем нужные даты
    date_to_select_start, date_to_select_end = date_previous()
    # date_to_select_start = "01-01-2024"
    # date_to_select_end = "15-01-2024"

    # Загрузка страницы
    driver_1.get(url)
    time.sleep(2)
    try:
        # Ждем появления кнопки "Согласен" в течение 10 секунд
        accept_button = WebDriverWait(driver_1, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[@class='btn2 btn2-primary' and contains(text(), 'Согласен')]")))
        # Если кнопка найдена, нажимаем на неё
        accept_button.click()
        print("Кнопка 'Согласен' найдена и нажата.")
    except TimeoutException:
        # Если кнопка не найдена в течение 10 секунд, выводим сообщение и продолжаем выполнение без нажатия
        print("Кнопка 'Согласен' не найдена.")

    # Выбор дат в календаре
    time.sleep(2)
    #  НАЧАЛО МЕСЯЦА
    try:
        # Ждем появления  в течение 10 секунд
        element = WebDriverWait(driver_1, 10).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/div[3]/div[4]/div/div/div[1]/div/div/div/div/div[4]/p[2]/a')))
        # Если найдена, нажимаем на неё
        element.is_selected()
        element.send_keys(Keys.TAB)  # Отправляем клавишу Tab к элементу

        print("Календарь   найден.")
    except TimeoutException:
        # Если  не найдена в течение 10 секунд, выводим сообщение и продолжаем выполнение
        print("Календарь  не найден.")

    time.sleep(2)

    # Копирование текста в буфер обмена
    pyperclip.copy(date_to_select_start)
    # нажатие Ctrl + V, вставка текста из буфера
    ActionChains(driver_1).key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()

    #  КОНЕЦ МЕСЯЦА
    try:
        # Ждем появления в течение 10 секунд
        element = WebDriverWait(driver_1, 10).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/div[3]/div[4]/div/div/div[1]/div/div/div/div/div[5]/form/div[2]/span/label')))
        # Если найдена, нажимаем на неё
        element.is_selected()
        element.send_keys(Keys.TAB)  # Отправляем клавишу Tab к элементу
        print("Календарь  найден.")
    except TimeoutException:
        # Если  не найдена в течение 10 секунд, выводим сообщение и продолжаем выполнение
        print("Календарь  не найден.")

    # Копирование текста в буфер обмена
    pyperclip.copy(date_to_select_end)
    # нажатие Ctrl + V, вставка текста из буфера
    ActionChains(driver_1).key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()

    #  Нажатие кнопки для выбора дат
    try:
        # Ждем появления кнопки  в течение 10 секунд
        accept_button = WebDriverWait(driver_1, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//*[@id='app']/form/div[4]/button/span")))
        # Если кнопка найдена, нажимаем на неё
        accept_button.click()
        print("Кнопка  найдена и нажата.")
    except TimeoutException:
        # Если кнопка не найдена в течение 10 секунд, выводим сообщение и продолжаем выполнение без нажатия
        print("Кнопка  не найдена.")

    # Ждем загрузки динамической таблицы
    # Ожидание появления элемента с помощью XPath
    element = WebDriverWait(driver_1, 10).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="app"]/div[1]/div[2]/div/div[2]/div[3]/table/tbody'))
    )
    # Получаем строки таблицы
    table_rows = element.find_elements(By.CSS_SELECTOR, "tr")
    return table_rows


#  создание таблицы и добавление заголовков
def create_table():
    # Создание новой книги
    wb_1 = xw.Book()
    # Добавление нового листа
    ws_1 = wb_1.sheets.add("Новый лист")
    # Добавление ЗАГОЛОВКОВ
    ws_1.range("A1").value = "Дата USD/RUB"
    ws_1.range("B1").value = "Курс USD/RUB"
    ws_1.range("C1").value = "Время USD/RUB"
    ws_1.range("D1").value = "Дата JPY/RUB "
    ws_1.range("E1").value = "Курс JPY/RUB "
    ws_1.range("F1").value = "Время JPY/RUB "
    return wb_1, ws_1


#  Получение данных первой страницы
def getting_page_data(table_rows, ws_1):
    if table_rows:
        # Проходимся по каждой строке таблицы
        for i, row in enumerate(table_rows, start=2):
            # Получаем текст ячеек в строке
            cells = row.find_elements(By.TAG_NAME, "td")
            row_data = [cell.text for cell in cells]
            print(row_data)
            if len(row_data) >= 5:  # Если в строке достаточно столбцов
                ws_1.range(f"A{i}").value = row_data[0]
                ws_1.range(f"B{i}").value = row_data[3]
                ws_1.range(f"C{i}").value = row_data[4]
    else:
        print("Таблица не найдена на странице.")
    return ws_1


#  Получение данных второй страницы
def getting_page_data_2(table_rows, ws_1):
    if table_rows:
        # Проходимся по каждой строке таблицы
        for i, row in enumerate(table_rows, start=2):
            # Получаем текст ячеек в строке
            cells = row.find_elements(By.TAG_NAME, "td")
            row_data = [cell.text for cell in cells]
            print(row_data)
            if len(row_data) >= 5:  # Если в строке достаточно столбцов
                ws_1.range(f"D{i}").value = row_data[0]
                ws_1.range(f"E{i}").value = row_data[3]
                ws_1.range(f"F{i}").value = row_data[4]
    else:
        print("Таблица не найдена на странице.")
    return ws_1


#  Добавление столбца "Результат"
def column_entry(ws_1):
    # Добавление заголовка для столбца "Результат"
    ws_1.range('G1').value = "Результат"
    # Получаем максимальный номер строки с данными в столбце A
    last_row = ws_1.range('A' + str(ws_1.cells.last_cell.row)).end('up').row
    # Начинаем со второй строки, так как первая строка - это заголовки
    for row in range(2, last_row + 1):
        # Получаем значения USD/RUB и JPY/RUB для текущей строки
        usd_rub_value = ws_1[f'B{row}'].value
        jpy_rub_value = ws_1[f'E{row}'].value
        # Проверка наличия данных
        if usd_rub_value == "-" or jpy_rub_value == "-":
            # Запись результата в столбец "Результат" (столбец G)
            ws_1[f'G{row}'].value = "-"
        elif usd_rub_value is not None and jpy_rub_value is not None and usd_rub_value != '-' and jpy_rub_value != '-':
            # Расчет результата (USD/RUB divided by JPY/RUB)
            result = float(usd_rub_value) / float(jpy_rub_value)
            # Запись результата в столбец "Результат" (столбец G)
            ws_1[f'G{row}'].value = result
    return ws_1


#  Форматирование столбцов по ширине и формат чисел
def format_setting_col(ws_1):
    # Авто ширина столбцов
    ws_1.autofit()
    # Установка формата чисел в столбцах B и E (USD/RUB и JPY/RUB)
    ws_1 = format_finance(ws_1, 'B')
    ws_1 = format_finance(ws_1, 'E')
    ws_1 = format_finance(ws_1, 'G')
    return ws_1


def format_finance(ws_2, column_letter='B'):
    # Определяем фактический диапазон данных в столбце B
    column_range = ws_2.range(column_letter + '1').expand('down')
    # Устанавливаем финансовый формат для столбца B
    for cell in column_range:
        if isinstance(cell.value, (int, float)):  # Проверяем, что значение является числом
            cell.value = "${:,.2f}".format(cell.value)  # Форматируем число как денежное значение
    return ws_2


#  Проверка авто суммы (Числа в столбце или нет)
def autosum_check(ws_1, column_letter='B'):
    # Находим последнюю заполненную строку в столбце
    last_row = ws_1.range(column_letter + str(ws_1.cells.last_cell.row)).end('up').row
    # Устанавливаем формулу автосуммы в ячейку под последним заполненным значением в столбце
    ws_1.cells(last_row + 1, column_letter).formula = '=SUM({}2:{}{})'.format(column_letter, column_letter, last_row)
    # Получаем значение из ячейки с формулой
    sum_value = ws_1.range(column_letter + str(last_row + 1)).value
    ws_1.range(column_letter + str(last_row + 1)).value = None
    # Проверка, что ячейки распознаются как числовой формат
    if is_number(sum_value):
        print('Ячейки распознаются как числовой формат')
        return True
    else:
        print('Ячейки не распознаются как числовой формат')
        return False


#  проверка на число
def is_number(n):
    return isinstance(n, (int, float, Decimal))


def get_rows_count(ws):
    last_row = ws.cells(ws.cells.last_cell.row, 1).end('up').row
    return last_row


def format_row_count(rows_count):
    if rows_count % 10 == 1 and rows_count % 100 != 11:
        return f'{rows_count} строка'
    elif 2 <= rows_count % 10 <= 4 and not (11 <= rows_count % 100 <= 14):
        return f'{rows_count} строки'
    else:
        return f'{rows_count} строк'


# Отправка файла на почту
def send_email_with_excel(wb, recipient_email, name_file):
    # Открываем соединение с SMTP-сервером
    smtp_server = 'smtp.mail.ru'  # адрес SMTP-сервера
    smtp_port = 587  # порт SMTP-сервера
    sender_email = 'makc.mon@mail.ru'  # адрес отправителя
    password = 'deRME9Y4BdnWTg92S5A1'  # пароль от почтового ящика отправителя

    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(sender_email, password)

    # Прикрепляем файл Excel
    wb_filename = name_file
    # Определяем количество строк в файле Excel
    ws = wb.sheets[0]  # Предполагается, что лист, содержащий данные, это первый лист
    rows_count = get_rows_count(ws)
    # Форматируем количество строк с правильным склонением
    rows_count_formatted = format_row_count(rows_count)

    wb.save(wb_filename)

    # Создаем письмо
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = f'В файле  {rows_count_formatted}'

    attachment = open(wb_filename, 'rb')
    part = MIMEBase('application', 'octet-stream')
    part.set_payload(attachment.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', "attachment; filename= " + wb_filename)
    msg.attach(part)

    # Отправляем письмо
    server.sendmail(sender_email, recipient_email, msg.as_string())

    # Закрываем соединение с SMTP-сервером
    server.quit()


#  Получение дат начала и конца предыдущего месяца
def date_previous():
    # 1. Определить текущую дату
    current_date = datetime.now()

    # 2. Вычислить дату начала предыдущего месяца
    first_day_of_current_month = current_date.replace(day=1)
    last_day_of_previous_month = first_day_of_current_month - timedelta(days=1)
    first_day_of_previous_month = last_day_of_previous_month.replace(day=1)

    # 3. Использовать эти даты для формирования запроса или фильтрации данных
    start_date = first_day_of_previous_month.strftime('%d.%m.%Y')
    end_date = last_day_of_previous_month.strftime('%d.%m.%Y')
    print("Начало предыдущего месяца:", start_date)
    print("Конец предыдущего месяца:", end_date)
    return start_date, end_date


def main():
    # URL страниц
    page_url = 'https://www.moex.com/ru/derivatives/currency-rate.aspx?currency=USD_RUB'
    page_url_2 = 'https://www.moex.com/ru/derivatives/currency-rate.aspx?currency=JPY_RUB'
    name_file = "table_data.xlsx"
    recipient_email = 'makc.mon@mail.ru'
    # Путь к драйверу браузера
    DRIVER_PATH = 'chromedriver.exe'

    # Запуск браузера
    service = Service(DRIVER_PATH)  # Инициализация драйвера браузера
    chrome_options = Options()
    driver = webdriver.Chrome(service=service)

    wb, ws = create_table()  # создание таблицы и добавление заголовков

    #  Получение данных первой страницы
    page_content = opening_web_page(page_url, driver)
    ws = getting_page_data(page_content, ws)  # Парсинг данных первой страницы
    #  Получение данных второй страницы
    page_content = opening_web_page(page_url_2, driver)
    ws = getting_page_data_2(page_content, ws)  # Парсинг данных второй страницы

    # столбец "РЕЗУЛЬТАТ"
    ws = column_entry(ws)  # Добавление результата в столбец G
    ws = format_setting_col(ws)  # Форматирование таблицы
    #  Проверка автосуммы (Числа в столбце или нет)
    flag = True
    for literal in ["B", "E", "G"]:
        if not autosum_check(ws, column_letter=literal):
            flag = False  # Если не числа в столбцах, прерываем
            break

    if flag:  # Если всё нормально отправляем на почту
        #  файл Excel отправляем по электронной почте
        send_email_with_excel(wb, recipient_email, name_file)

    input("Нажмите Enter для завершения работы и закрытия браузера")
    driver.quit()  # Закрытие драйвера после использования
    if wb:
        wb.close()  # Закрываем книгу
    print("Работа окончена!")
    # Удаляем файл после отправки
    os.remove(name_file)


if __name__ == "__main__":
    main()
