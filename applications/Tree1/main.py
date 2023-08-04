from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QIcon, QPalette, QColor

from connect1 import Connect1
from widget1 import Widget1
import sys
import res_1_rc

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    window = Widget1(None)
    window.setWindowTitle('Представление в виде дерева')
    pal1 = QPalette()
    pal1.setColor(window.backgroundRole(), QColor("lightGray"))  # установка фона для окна
    window.setPalette(pal1)

    window.setWindowIcon(QIcon(":/img2.png"))     # установка эмблеммы в окно
    window.show()

    sys.exit(app.exec())
