#
# Первый вариант с библиотекой playwright
#

import os
import time
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import xlwings as xw
from decimal import Decimal
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders


#  Открытие веб страницы
def opening_web_page(url, browser_1):
    # Открытие новой страницы
    page = browser_1.new_page()
    # Переход на страницу
    page.goto(url)
    time.sleep(2)  # Adjust the delay time as needed
    # Получение данных страницы
    page_content_1 = page.content()
    return page_content_1


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
def getting_page_data(page_content_1, ws_1):
    # Обработка извлеченного контента с помощью BeautifulSoup
    soup = BeautifulSoup(page_content_1, features="html.parser")  # Specify HTML parser
    tables = soup.find_all("tbody")
    if tables:
        for table in tables:
            # Ищем все строки таблицы
            rows = table.find_all("tr")
            for i, row in enumerate(rows, start=2):
                # Извлечение текста из каждой ячейки
                row_data = [cell.get_text(strip=True) for cell in row.find_all(["th", "td"])]
                if len(row_data) >= 5:  # Если в строке достаточно столбцов
                    ws_1.range(f"A{i}").value = row_data[0]
                    ws_1.range(f"B{i}").value = row_data[3]
                    ws_1.range(f"C{i}").value = row_data[4]
    else:
        print("Таблица не найдена на странице.")
    return ws_1


#  Получение данных второй страницы
def getting_page_data_2(page_content_1, ws_1):
    # Обработка извлеченного контента с помощью BeautifulSoup
    soup = BeautifulSoup(page_content_1, features="html.parser")  # HTML парсер
    tables = soup.find_all("tbody")
    if tables:
        for table in tables:
            # Ищем все строки таблицы
            rows = table.find_all("tr")
            for i, row in enumerate(rows, start=2):
                # Извлечение текста из каждой ячейки
                row_data = [cell.get_text(strip=True) for cell in row.find_all(["th", "td"])]
                if len(row_data) >= 5:  # Если в строке достаточно столбцов
                    # Добавление данных в новые столбцы
                    ws_1.range(f"D{i}").value = row_data[0]
                    ws_1.range(f"E{i}").value = row_data[3]
                    ws_1.range(f"F{i}").value = row_data[4]
                    # print(row_data)
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
    smtp_server = 'smtp.mail.ru'  #  адрес SMTP-сервера
    smtp_port = 587  #  порт SMTP-сервера
    sender_email = 'makc.mon@mail.ru'  #  адрес отправителя
    password = '***************'  #  пароль от почтового ящика отправителя

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



#  синхронизированная версия Playwright
with sync_playwright() as p:
    # URL страниц
    page_url = 'https://www.moex.com/ru/derivatives/currency-rate.aspx?currency=USD_RUB'
    page_url_2 = 'https://www.moex.com/ru/derivatives/currency-rate.aspx?currency=JPY_RUB'
    name_file = "table_data.xlsx"
    recipient_email = 'makc.mon@mail.ru'

    # Запуск браузера
    browser = p.chromium.launch()
    # создание таблицы и добавление заголовков
    wb, ws = create_table()

    #  Получение данных первой страницы
    page_content = opening_web_page(page_url, browser)
    # Парсинг данных первой страницы
    ws = getting_page_data(page_content, ws)

    #  Получение данных второй страницы
    page_content = opening_web_page(page_url_2, browser)
    # Парсинг данных второй страницы
    ws = getting_page_data_2(page_content, ws)

    #  Добавление результата в столбец G
    ws = column_entry(ws)
    # Форматирование таблицы
    ws = format_setting_col(ws)
    #  Проверка автосуммы (Числа в столбце или нет)
    flag = True
    for literal in ["B", "E", "G"]:
        if not autosum_check(ws, column_letter=literal):
            flag = False   # Если не числа в столбцах, прерываем
            break

    if flag:  # Если всё нормально отправляем на почту
        #  файл Excel отправляем по электронной почте
        send_email_with_excel(wb, recipient_email, name_file)

    # Закрываем книгу
    wb.close()
    # ЗАКРЫВАЕМ БРАУЗЕР
    browser.close()
    # Удаляем файл после отправки
    os.remove(name_file)
