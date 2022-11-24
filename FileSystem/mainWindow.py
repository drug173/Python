from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QWidget, QMainWindow, QVBoxLayout, QLabel, QFileSystemModel
from PyQt5.QtGui import QPalette, QColor

from FileSystemView import Ui_MainWindow


class MainWindow1(QMainWindow):

    def __init__(self, parent=None):
        super(MainWindow1, self).__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.treeView.setUniformRowHeights(True)
        model = QFileSystemModel()
        model.setRootPath('')
        self.ui.treeView.setModel(model)
