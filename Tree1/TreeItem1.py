from PyQt5.QtCore import qDebug, QVariant


class TreeItem1(object):

    def __init__(self, data1=None, parent=None):
        self.__parent_item = parent  # родитель узла
        self.__item_data = data1  # данные узла
        self.__child_items = list()  # список дочерних элементов узла

    def childCount(self) -> int:
        """Количество дочерних элементов  тип int"""
        return len(self.__child_items)

    def child(self, row):
        """Получение потомка по строке тип TreeItem1"""
        i = self.__child_items[row]
        return i

    def parentItem(self):
        """возвращает родительский узел тип  TreeItem1"""
        return self.__parent_item

    def rowNumber(self) -> int:
        """
            возвращает свой номер  в списке потомков своего родителя тип int
        """
        if self.__parent_item:
            return self.__parent_item.__child_items.index(self)
        else:
            return 0

    def appendChild(self, item):
        """
            добавляет потомка  (узел в список потомков)
        """
        self.__child_items.append(item)

    def insertChild(self, row: int, count: int, columns: int):
        if row < 0 or row > len(self.__child_items):
            return False
        data = [0, None, 0, 0, 0]
        for rowNum in range(count):
            item = TreeItem1(data, self)

            self.appendChild(item)
        return True


    def data(self, column):
        """Получить данные из нужного столбца"""
        col = column
        ddd=self.__item_data[column]
        # print(col)
        if column < 0 or column >= len(self.__item_data):
            return QVariant()
        return self.__item_data[column]

    def setData(self, column, value):
        """метод ставит значение value в столбец column
        элемента при редактированиии(изменении) элемента тип  bool"""
        if column < 0 or column >= len(self.__item_data):
            return False
        self.__item_data[column] = value
        return True

    def removeChild(self, row):
        """удаляет потомка по номеру в списке потомков тип  bool"""
        self.__child_items.pop(row)
        return True
