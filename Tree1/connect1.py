import sqlite3
import sys

from PyQt5 import QtSql
from PyQt5.QtCore import QFile
from PyQt5.QtSql import QSqlDatabase
from PyQt5.QtWidgets import QMessageBox


class Connect1:

    def __init__(self, name1):
        self.con = None
        self.name = name1  # устанавливаем имя базы данных

    @property
    def connect_to_data_base(self):
        # self.name = 'W:\none'
        con = QtSql.QSqlDatabase.addDatabase('QSQLITE')
        con.setDatabaseName(self.name)
        if not con.open():
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Ошибка открытия БД")
            retval = msg.exec_()
            return sys.exit(1)
        self.con = con

    def close_db(self):
        self.con.close()
