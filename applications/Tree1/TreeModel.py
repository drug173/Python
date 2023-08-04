import typing

from PyQt5 import Qt
from PyQt5.QtCore import QAbstractItemModel, QModelIndex, pyqtSignal, QVariant, QByteArray, QSize, QObject
from PyQt5.QtGui import QColor, QPixmap, QIcon
from PyQt5.QtSql import QSqlQuery

from TreeItem1 import TreeItem1


class TreeModel(QAbstractItemModel):
    def __init__(self, parent: QObject = None):
        super().__init__(parent)
        self.rootItem = TreeItem1(["1", "2", "3", "4", "5"])
        """ корневой узел"""
        self.setDataModel(self.rootItem)

#------------

    def __del__(self):
        pass

    def columnCount(self, parent: QModelIndex = ...) -> int:
        """ количество столбцов  всегда равно 5"""
        return 5

    def rowCount(self, parent: QModelIndex = ...):
        """ количество детей у элемента"""
        parent_item = self.getItem(parent)
        return parent_item.childCount()

    def getItem(self, index1: QModelIndex):
        """  Ссылка  на элемент по индексу """
        if index1.isValid():
            item = index1.internalPointer()    ######  Непонятно как работает  #############################
            if item:
                return item
        return self.rootItem

    def setDataModel(self, parent: TreeItem1 = ...):
        """ устанавливает данные из таблицы базы данных в модель дерева"""
        mapId = {}  # список словарей  хранит id и id_parent элементов
        idList = list()  # хранит все id элементов
        query1 = QSqlQuery()
        idItem = None
        idParenItem = None
        query1.exec("SELECT * FROM hierarhy;")
        while query1.next():  # составляем список id всех элементов и родителей
            idItem = int(query1.value(0))
            val1 = query1.value(1)
            if val1 == '':
                idParenItem = 0
            else:
                idParenItem = int(query1.value(1))
            idList.append(idItem)
            mapId[idItem] = idParenItem
        query1.clear()
        #  ищем корни дерева (может быть несколько корней)
        fl = False
        value = None
        if len(mapId) > 0:
            for keyId in mapId:  # перебираем значения словаря id_parent

                value = mapId[keyId]

                fl = False
                for j in range(0, len(idList), 1):
                    if value == idList[j]:  # проверяем есть ли родитель у элемента
                        fl = True
                        break  # если родитель есть, переходим к другому
                if not fl:  # если родителя нет, то узел - корень дерева
                    # создаём узел, выбираем из базы запись с id==dicList.keys()
                    query1.prepare("SELECT * FROM hierarhy WHERE id =?;")
                    query1.addBindValue(keyId)
                    query1.exec()
                    query1.next()
                    DataItemColumn = list()  # Cписок данных строки по столбцам
                    DataItemColumn.append(str(query1.value(2)))
                    DataItemColumn.append(query1.value(3))
                    www = query1.value(3)
                    DataItemColumn.append(int(query1.value(0)))
                    val2 = query1.value(1)
                    if val2 == '':
                        DataItemColumn.append(0)
                    else:
                        DataItemColumn.append(int(val2))
                    val2 = query1.value(4)
                    if val2 == '':
                        DataItemColumn.append(0)
                    else:
                        DataItemColumn.append(int(val2))
                    # print(type(query1.value(3)))
                    parentindex = self.index(0, 0, QModelIndex())  # получаем индекс корня rootItem
                    item = TreeItem1(DataItemColumn, parent)  # Создаёт новый узел дерева
                    parent.appendChild(item)  # Добавляет новый узел  в потомки текущего  родителя
                    query1.clear()
                    self.addChild(mapId, keyId, item)
                    mapId[keyId] = -1

    def addChild(self, mapId: dict, key: int, parent: TreeItem1):
        """ рекурсивная функция добавления потомков для узла с id равным key """
        if len(mapId) > 0:  # если словарь <id,Id_parent> не пуст
            value2 = None
            query3 = QSqlQuery()
            rowItems = list()  # спиок данных в строке по столбцам
            for key2 in mapId:  # перебираем значения словаря записей таблицы данных
                value2 = mapId[key2]
                if value2 == key:  # проверяем является ли узел value2 родителем текущему узлу key
                    query3.prepare("SELECT * FROM hierarhy WHERE id =?;")
                    query3.addBindValue(key2)
                    query3.exec()
                    query3.next()
                    DataItemColumn = list()  # Cписок данных строки по столбцам
                    DataItemColumn.append(str(query3.value(2)))
                    DataItemColumn.append(query3.value(3))  #-------------------
                    www = query3.value(3)
                    DataItemColumn.append(int(query3.value(0)))
                    DataItemColumn.append(int(query3.value(1)))
                    DataItemColumn.append(int(query3.value(4)))
                    # print(type(query3.value(3)))
                    item = TreeItem1(DataItemColumn, parent)  # создаём новый узел дерева
                    query3.clear()
                    parent.appendChild(item)  # добавляем узел нового родителя в потомки корня
                    self.addChild(mapId, key2, item)  # вызываем рекурсивную функцию добавления потомков в текущий узел

    def data(self, index: QModelIndex, role: int = ...) -> typing.Any:
        """  получить данные из модельного индекса index с ролью role """
        if not index.isValid():
            return QVariant()
        if role != Qt.Qt.DisplayRole and role != Qt.Qt.EditRole and role != Qt.Qt.BackgroundRole and role != Qt.Qt.DecorationRole:
            return QVariant()
        item = self.getItem(index)
        if role == Qt.Qt.BackgroundRole and index.column() == 0:
            state = int(item.data(4))
            if state == 0:
                return QColor(Qt.Qt.red)
            if state == 1:
                return QColor(Qt.Qt.yellow)
            if state == 2:
                return QColor(Qt.Qt.green)
            return QColor(Qt.Qt.lightGray)
        if role == Qt.Qt.DecorationRole and index.column() == 1:
            item = self.getItem(index)
            pix1 = QByteArray()
            pix = item.data(1)
            if not isinstance(pix, QByteArray):
                pix = QByteArray()
            # print(pix)
            pixMap = QPixmap()
            pixMap.loadFromData(pix)
            size = QSize(55, 55)
            icon = QIcon(pixMap)
            icon.pixmap(size)
            return icon
        if role == Qt.Qt.DisplayRole:
            if index.column() == 0 or index.column() == 3 or index.column() == 2 or index.column() == 4:
                return item.data(index.column())
        return QVariant()

    def index(self, row: int, column: int, parent: QModelIndex = ...) -> QModelIndex:
        """ индекс модели по заданным строке, столбцу и родителю """
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()

        childItem = parentItem.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QModelIndex()

    def parent(self, index: QModelIndex) -> QModelIndex:
        """  индекс родителя  по индексу  текущего узла"""
        if not index.isValid():
            return QModelIndex()
        childItem = self.getItem(index)
        parentItem = childItem.parentItem()
        if parentItem == self.rootItem:
            return QModelIndex()
        return self.createIndex(parentItem.rowNumber(), 0, parentItem)

    def setData(self, index: QModelIndex, value: typing.Any, role: int = ...) -> bool:
        """ добавляет данные в узел при добавлении вручную """
        if role != 0 and role != 1 and role != 8:
            return False
        item = self.getItem(index)
        colcol = index.column()
        result = item.setData(index.column(), value)
        bb = result
        if result:
            self.dataChanged.emit(index, index)
        return result

    def insertRows(self, row: int, count: int, parent: QModelIndex = ...) -> bool:
        success = False
        if count < 1 or row < 0 or row > self.rowCount(parent) or parent.column() > 0:
            return False
        self.beginInsertRows(parent, row, row + count - 1)
        parentItem = self.getItem(parent)
        while count > 0:
            if parentItem:
                success = parentItem.insertChild(row, count, 5) # вставляет новый узел в конец списка потомков
            else:
                success = self.rootItem.insertChild(row, count, 5)
            count -= 1
        self.endInsertRows()
        return success

    def setItemData(self, index: QModelIndex, roles: typing.Dict[int, typing.Any]) -> bool:
        """  добавляет данные в столбец строки при добвлении вручную """
        b = True
        for role in roles:
            r = roles[role]
            b = b and self.setData(index, roles[role], role)
        return b

    def removeRows(self, position: int, rows: int, parent: QModelIndex = ...):
        parentItem = self.getItem(parent)
        success = True
        self.beginRemoveRows(parent, position, position + rows - 1)
        success = parentItem.removeChild(position)
        self.endRemoveRows()
        return success

    def beginResetModel1(self):
        self.beginResetModel()

    def endResetModel1(self):
        self.endResetModel()
