from PyQt5.QtCore import QModelIndex, pyqtSignal, pyqtSlot, QVariant, QFile, QByteArray, QBuffer, QIODevice, QSize, \
    QItemSelectionModel, QItemSelection
from PyQt5.QtGui import QPixmap, QFont, QIcon
from PyQt5.QtSql import QSqlQuery
from PyQt5.QtWidgets import QWidget, QApplication, QLabel, QDialog, QMessageBox

from TreeModel import TreeModel
from inputdialog import InputDialog
from connect1 import Connect1
from newForm import *

class Widget2(QWidget):
    def __init__(self):
        super().__init__()
        self.db = None
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.setFixedSize(600, 400)
        self.setWindowTitle("Лейман М.А.")
        label = QLabel(self)
        label.move(25, 25)
        label.setFixedSize(550, 350)
        label.setStyleSheet('background-color: rgb(180, 190, 200)')
        label.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        label.setFont(QFont('Arial', 15))
        label.setWordWrap(True)
        label.setText('Тестовая программа\n \nПостроение из базы данных иерархического списка\n в виде дерева,'
                      'с возможностью редактирования\n и добавления дочерних элементов. \n \n \n '
                      ' выполнил: Лейман М.А.\n тел: +79613224543\n email: makc.mon@mail.ru')
        self.setWindowFlags(QtCore.Qt.Dialog)  # делает окно несворачиваемым        


class Widget1(QtWidgets.QWidget):
    valueChangedSignal = pyqtSignal(list)
    valueInsertSignal = pyqtSignal(list)

    def __init__(self, parent):
        QtWidgets.QWidget.__init__(self, parent)
        self.idRowNew = None  # id новой (вставляемой) строки
        self.__iDialog = None
        self.w = None
        self.y = None
        self.ui = Ui_Widget()
        pixmap = QPixmap(":/img2.png")  # установка эмблеммы в окно
        self.ui.setupUi(self)
        self.ui.label_2.setPixmap(pixmap)
        self.ui.label.setPixmap(pixmap)
        self.ui.treeView.setAttribute(QtCore.Qt.WA_StyledBackground, True)
        self.ui.treeView.setStyleSheet('background-color: rgb(170, 190,195)')  # установка фона для окна дерева
        self.ui.button.setToolTip("<h3>Нажми меня</h3>")
        self.ui.button.setStyleSheet("background-color : rgb(10, 120, 10)")
        self.db = Connect1("task")
        cursor = self.db.connect_to_data_base
        treemodel = TreeModel()
        self.ui.treeView.setModel(treemodel)
        self.ui.button.clicked.connect(self.window_open)  # открывает окно "О программе" +
        self.ui.delRow.clicked.connect(self.removeRowTree)  # удаляет строку (узел) с дочерними строками +
        self.ui.modifi.clicked.connect(self.modifiRow)  # изменяет данные строки (узла) -
        self.ui.addRow.clicked.connect(self.insertChildTree)  # Добавляет строку (Узел) -
        self.ui.treeView.selectionModel().selectionChanged[QItemSelection, QItemSelection].connect(self.updateActions)
        self.ui.treeView.selectionModel().currentRowChanged[QModelIndex, QModelIndex].connect(self.slotCurrentPic)
        self.valueChangedSignal[list].connect(self.editDataBase)    # Изменяет выбранный элемент  в БАЗЕ
        self.valueInsertSignal[list].connect(self.insertDataBase)  # вставляем  новые данные в БАЗУ

        self.ui.treeView.setColumnHidden(2, True) # делает невидимым столбцы 2,3,4
        self.ui.treeView.setColumnHidden(3, True)
        self.ui.treeView.setColumnHidden(4, True)
        header = self.ui.treeView.header()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.Fixed)
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.Fixed)
        header.setSectionResizeMode(4, QtWidgets.QHeaderView.Fixed)
        header.setStretchLastSection(False)
        self.updateActions()

    def window_open(self):
        self.w = Widget2()
        self.w.show()
        # self.hide()

    def closeEvent(self, event):
        self.db.close_db()
        for window in QApplication.topLevelWidgets():
            window.close()

    def slotCurrentPic(self, index: QModelIndex):

        yurModel = self.ui.treeView.model()
        item = yurModel.getItem(index)
        pix = item.data(1)
        if not isinstance(pix, QByteArray):
            # sss = QByteArray(item.data(1).encode())
            sss = ":/img2.png"
            outPixmap = QPixmap(sss)
            pixmap = outPixmap.scaledToWidth(200)
        else:
            sss = pix
            outPixmap = QPixmap()
            outPixmap.loadFromData(sss)
            dd = outPixmap.width()
            pixmap = outPixmap.scaledToWidth(200)
        self.ui.label.setPixmap(pixmap)

    @pyqtSlot()
    def insertChildTree(self):
        pInputDialog = InputDialog()
        if pInputDialog.flag:
            name = pInputDialog.name()  # вводим данные
            image = pInputDialog.image()
            state = pInputDialog.state()
            var = pInputDialog.destroyed
            index = self.ui.treeView.selectionModel().currentIndex()  # Получаем модельный индекс элемента
            model = self.ui.treeView.model()  #  получаем модель дерева
            colCount = model.columnCount(index)
            itemParent = model.getItem(index)  # получаем выбранный элемент, он становится родителем вставляемого элемента
            idParentRow = int(itemParent.data(2))  # получаем id выбранной строки, становится id_parent для вставляемого элемента
            newValue = list()
            newValue.append(name)
            newValue.append(image)
            newValue.append(state)
            newValue.append(idParentRow)
            self.valueInsertSignal.emit(newValue)  # отправляем сигнал на запись данных в БД
            newValue.clear()
            query2 = QSqlQuery()  # получаем изображение
            query2.prepare("SELECT * FROM  hierarhy  WHERE id =?;")
            query2.addBindValue(self.idRowNew)
            query2.exec()
            query2.next()
            image2 = query2.value(3)
            query2.clear()
            newValue.append(name)
            newValue.append(image2)
            newValue.append(self.idRowNew)
            newValue.append(idParentRow)
            newValue.append(state)
            rowNew = model.rowCount(index)
            if not model.insertRow(rowNew, index):
                return
            dictRole = (0, 1, 0, 0, 0)
            for column in range(colCount):
                indexChild = model.index(rowNew, column, index)  # индекс  вставляемого элемента в модели
                model.setData(indexChild, newValue[column], dictRole[column])      # вставляем данные  в столбец модели по индексу
            self.ui.treeView.selectionModel().reset()
            self.updateActions()

    def updateActions(self):
        hasSelection = not self.ui.treeView.selectionModel().selection().isEmpty()
        self.ui.delRow.setEnabled(hasSelection)
        self.ui.modifi.setEnabled(hasSelection)

    @pyqtSlot()
    def modifiRow(self):
        pInputDialog = InputDialog()
        if pInputDialog.flag:
            name = pInputDialog.name()  # вводим данные
            image = pInputDialog.image()
            state = pInputDialog.state()
            var = pInputDialog.destroyed
            index = self.ui.treeView.selectionModel().currentIndex()  # модельный индекс элемента
            model = self.ui.treeView.model()
            item2 = model.getItem(index)     # выбранный элемент
            rowItem = item2.rowNumber()        # номер строки элемента  в родительском узле
            idRow = int(item2.data(2))      #  id выбранной строки
            idRowParent = int(item2.data(3))  #  id_parent выбраной строки
            parent = model.parent(index)      # индекс родителя
            newValue = list()
            newValue.append(name)
            newValue.append(image)
            newValue.append(state)
            newValue.append(idRow)
            self.valueChangedSignal.emit(newValue)  # отправляем сигнал на запись данных в БД
            newValue.clear()
            query2 = QSqlQuery()  # получаем изображение
            query2.prepare("SELECT * FROM  hierarhy  WHERE id =?;")
            query2.addBindValue(idRow)
            query2.exec()
            query2.next()
            image2 = query2.value(3)
            query2.clear()
            newValue.append(name)
            newValue.append(image2)
            newValue.append(idRow)
            newValue.append(idRowParent)
            newValue.append(state)
            model.beginResetModel1()  # Изменяем данные в строке
            colCount = model.columnCount(index)
            dictRole = (0, 1, 0, 0, 0)
            for column in range(colCount):
                indexInsert = model.index(rowItem, column, parent)  # УЗНАТЬ СТРОКУ Изменяемого (ТЕКУЩЕГО) ЭЛЕМЕНТА
                model.setData(indexInsert, newValue[column], dictRole[column])
            model.endResetModel1()
            newValue.clear()
        self.updateActions()
        var = pInputDialog.destroyed

    def removeRowTree(self):
        """   удаляет строку со всеми зависимыми строками """
        model = self.ui.treeView.model()
        index = self.ui.treeView.selectionModel().currentIndex()  # Получаем модельный индекс выбранного элемента
        self.remoweItemRows(index, model)
        self.ui.treeView.selectionModel().reset()
        self.updateActions()

    def remoweItemRows(self, index: QModelIndex, model: TreeModel):  # удаляет элементы из списка детей
        item = model.getItem(index)
        childCountItem = item.childCount() # количество детей у элемента
        numRow = item.rowNumber()    #  номер строки элемента
        indexParent = model.parent(index) # индекс родителя элемента
        if childCountItem > 0:
            for numRowChild in range(childCountItem - 1, - 1, -1):
                indexChild = model.index(numRowChild, 0, index)
                self.remoweItemRows(indexChild, model)     #  каскадное удаление  потомков потомка
        idRow = int(item.data(2))  # получаем id строки
        if not model.hasChildren(index):  # если нет потомков, то удаляем узел
            query2 = QSqlQuery()
            query2.prepare("DELETE FROM  hierarhy  WHERE id =?;")
            query2.addBindValue(idRow)
            query2.exec()
            query2.clear()
        model.removeRow(numRow, indexParent)     #  Удаляем текущий узел после удаления  всех детей

    @pyqtSlot(list)
    def insertDataBase(self, newValue: list):
        """ вставляет новые данные в базу"""
        strName = str(newValue[0])
        if strName == '':
            return
        strImg1 = str(newValue[1])
        file = QFile(strImg1)  # создаем объект класса QFile
        dataImg = QByteArray()  # куда будем считывать данные
        # inBuffer = QBuffer(dataImg)
        if file.open(QIODevice.ReadOnly):  # Проверяем, возможно ли открыть наш файл для чтения
            dataImg = file.readAll()  # считываем данные
        query3 = QSqlQuery()
        query3.exec("INSERT INTO hierarhy (id_parent,name,image,state) VALUES (?, ?, ?, ?)")
        strIdParent = int(newValue[3])
        query3.addBindValue(strIdParent)
        query3.addBindValue(strName)
        query3.addBindValue(dataImg)
        strState = str(newValue[2])
        query3.addBindValue(strState)
        query3.exec()
        self.idRowNew = int(query3.lastInsertId())
        query3.clear()

    @pyqtSlot(list)
    def editDataBase(self, newValue: list):
        strName = str(newValue[0])
        if strName == '':
            return
        strImg1 = newValue[1]
        file = QFile(strImg1)  # создаем объект класса QFile
        dataImg = QByteArray()  # куда будем считывать данные
        if file.open(QIODevice.ReadOnly):  # Проверяем, возможно ли открыть наш файл для чтения
            dataImg = file.readAll()
        query3 = QSqlQuery()
        query3.prepare("UPDATE hierarhy SET name=?, image=?, state=? WHERE id =?;")
        strName = str(newValue[0])
        query3.addBindValue(strName)
        query3.addBindValue(dataImg)
        strState = str(newValue[2])
        query3.addBindValue(strState)
        idRow = int(newValue[3])
        query3.addBindValue(idRow)
        query3.exec()
        query3.next()
        if not query3.isActive():
            QMessageBox.warning(self, "Database Error", query3.lastError().text())
