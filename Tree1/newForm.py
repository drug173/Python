# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'newForm.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSignal, QModelIndex
from PyQt5.QtGui import QPixmap


class Ui_Widget(object):
    # currentSelectionSignal = pyqtSignal(QModelIndex, QModelIndex)

    def setupUi(self, Widget):
        Widget.setObjectName("Widget")
        Widget.resize(800, 600)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(Widget)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setContentsMargins(5, 5, 5, 5)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setContentsMargins(5, 5, 5, 5)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setContentsMargins(0, 5, 7, 5)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.button = QtWidgets.QPushButton(Widget)
        self.button.setObjectName('button')
        self.verticalLayout_2.addWidget(self.button)
        self.label_2 = QtWidgets.QLabel(Widget)
        self.label_2.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop)
        self.label_2.setWordWrap(False)
        self.label_2.setObjectName("label_2")
        self.verticalLayout_2.addWidget(self.label_2)
        self.label = QtWidgets.QLabel(Widget)
        self.label.setAlignment(QtCore.Qt.AlignTop)
        self.label.setWordWrap(False)
        self.label.setObjectName("label")
        self.verticalLayout_2.addWidget(self.label)
        self.verticalLayout_2.addStretch(1)
        self.horizontalLayout.addLayout(self.verticalLayout_2)
        self.treeView = QtWidgets.QTreeView(Widget)
        self.treeView.setObjectName("treeView")
        self.horizontalLayout.addWidget(self.treeView)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")

        self.addRow = QtWidgets.QPushButton(Widget)
        self.addRow.setObjectName("addRow")
        self.addRow.setStyleSheet("background-color : rgb(80, 190, 70)")
        self.horizontalLayout_3.addWidget(self.addRow)
        self.modifi = QtWidgets.QPushButton(Widget)
        self.modifi.setObjectName("modifi")
        self.horizontalLayout_3.addWidget(self.modifi)
        self.modifi.setStyleSheet("background-color : rgb(60, 160, 160)")
        self.delRow = QtWidgets.QPushButton(Widget)
        self.delRow.setObjectName("delRow")
        self.horizontalLayout_3.addWidget(self.delRow)
        self.delRow.setStyleSheet("background-color : rgb(240, 5, 5)")
        self.horizontalLayout_3.addStretch(1)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_2.addLayout(self.verticalLayout)



        self.retranslateUi(Widget)
        QtCore.QMetaObject.connectSlotsByName(Widget)



    def retranslateUi(self, Widget):
        _translate = QtCore.QCoreApplication.translate
        #Widget.setWindowTitle(_translate("Widget", "Widget"))
        self.button.setText('О программе')
        self.label_2.setText(_translate("Widget", "TextLabel2"))
        self.label.setText(_translate("Widget", "TextLabel1"))
        self.addRow.setText(_translate("Widget", "Добавить"))
        self.modifi.setText(_translate("Widget", "Изменить"))
        self.delRow.setText(_translate("Widget", "Удалить"))

# if __name__ == "__main__":
#     import sys
#     app = QtWidgets.QApplication(sys.argv)
#     Widget = QtWidgets.QWidget()
#     ui = Ui_Widget()
#     ui.setupUi(Widget)
#     Widget.show()
#     sys.exit(app.exec_())
