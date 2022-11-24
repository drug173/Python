from PyQt5.QtCore import pyqtSlot, pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QDialog, QLabel, QGridLayout, QLineEdit, QPushButton, QFileDialog, QComboBox


class InputDialog(QDialog):
    getIdRow = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.__strImg = "Изображение"
        self.__m_Name = QLineEdit()
        self.__m_Image = QLineEdit()
        self.__m_State = QComboBox()
        # self.__m_State = QLineEdit()
        self.flag = False
        self.setWindowTitle("Введите данные")
        self.plblName = QLabel("&name")
        self.plblImage = QLabel("&image")
        self.plblState = QLabel("&state")
        self.plblImg = QLabel("")
        self.plblImg.setText(self.__strImg)
        self.plblName.setBuddy(self.__m_Name)
        self.plblImage.setBuddy(self.__m_Image)
        self.plblState.setBuddy(self.__m_State)
        self.__m_State.addItem('0')
        self.__m_State.addItem('1')
        self.__m_State.addItem('2')
        self.pcmdCancel = QPushButton("Cancel")
        self.pcmdOpen = QPushButton("Открыть")
        self.pcmdOk = QPushButton("Ok")

        self.ptopLayout = QGridLayout()
        self.ptopLayout.addWidget(self.plblName, 0, 0)
        self.ptopLayout.addWidget(self.plblImage, 2, 0)
        self.ptopLayout.addWidget(self.plblState, 1, 0)
        self.ptopLayout.addWidget(self.__m_Name, 0, 1)
        self.ptopLayout.addWidget(self.__m_State, 1, 1)
        self.ptopLayout.addWidget(self.plblImg, 2, 1)
        self.ptopLayout.addWidget(self.pcmdOpen, 2, 2)
        self.ptopLayout.addWidget(self.pcmdOk, 3, 0)
        self.ptopLayout.addWidget(self.pcmdCancel, 3, 1)
        self.setLayout(self.ptopLayout)

        self.pcmdOpen.clicked.connect(self.openFile)
        self.pcmdOk.clicked.connect(self.okEnter)
        self.pcmdCancel.clicked.connect(self.cancelEnter)

        self.exec()

    @pyqtSlot()
    def openFile(self):
        """ слот загрузки файла изображения"""
        self.__strImg = QFileDialog.getOpenFileName(self, "Выберите файл изображения", "home", "Images (*.png)")
        self.plblImg.setText(self.__strImg[0])

    @pyqtSlot()
    def okEnter(self):
        self.flag = True
        self.close()


    @pyqtSlot()
    def cancelEnter(self):
        self.flag = False
        self.close()

    def name(self):
        if not self.__m_Name.text():
            self.flag = False
            self.close()
            return ''
        return self.__m_Name.text()

    def image(self):
        return self.__strImg[0]

    def state(self):
        return int(self.__m_State.currentText())

    def closeEvent(self, event):
        self.close()
