from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QWidget, QMainWindow, QApplication
import sys
from mainWindow import MainWindow1

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow1()
    # window.setWindowTitle('Представление в виде дерева')

    window.show()

    sys.exit(app.exec())
