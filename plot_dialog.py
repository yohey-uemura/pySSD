# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'plot_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(969, 644)
        self.pushButton = QtWidgets.QPushButton(Dialog)
        self.pushButton.setGeometry(QtCore.QRect(820, 580, 121, 41))
        self.pushButton.setObjectName("pushButton")
        self.widget = QtWidgets.QWidget(Dialog)
        self.widget.setGeometry(QtCore.QRect(30, 110, 901, 451))
        self.widget.setObjectName("widget")
        self.comboBox = QtWidgets.QComboBox(Dialog)
        self.comboBox.setGeometry(QtCore.QRect(40, 20, 801, 31))
        self.comboBox.setObjectName("comboBox")
        self.doubleSpinBox_LE = QtWidgets.QDoubleSpinBox(Dialog)
        self.doubleSpinBox_LE.setGeometry(QtCore.QRect(280, 67, 151, 24))
        self.doubleSpinBox_LE.setDecimals(1)
        self.doubleSpinBox_LE.setMaximum(500000.0)
        self.doubleSpinBox_LE.setObjectName("doubleSpinBox_LE")
        self.doubleSpinBox_HE = QtWidgets.QDoubleSpinBox(Dialog)
        self.doubleSpinBox_HE.setGeometry(QtCore.QRect(500, 67, 151, 24))
        self.doubleSpinBox_HE.setDecimals(1)
        self.doubleSpinBox_HE.setMaximum(500000.0)
        self.doubleSpinBox_HE.setObjectName("doubleSpinBox_HE")
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(220, 70, 51, 20))
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_2.setGeometry(QtCore.QRect(440, 70, 51, 20))
        self.label_2.setObjectName("label_2")
        self.comboBox_Ftype = QtWidgets.QComboBox(Dialog)
        self.comboBox_Ftype.setGeometry(QtCore.QRect(670, 65, 171, 31))
        self.comboBox_Ftype.setObjectName("comboBox_Ftype")
        self.pB_copy_for_all = QtWidgets.QPushButton(Dialog)
        self.pB_copy_for_all.setGeometry(QtCore.QRect(30, 570, 211, 41))
        self.pB_copy_for_all.setObjectName("pB_copy_for_all")
        self.pB_refresh = QtWidgets.QPushButton(Dialog)
        self.pB_refresh.setGeometry(QtCore.QRect(860, 20, 80, 80))
        self.pB_refresh.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("rotate360anticlockwise2red.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pB_refresh.setIcon(icon)
        self.pB_refresh.setIconSize(QtCore.QSize(48, 48))
        self.pB_refresh.setObjectName("pB_refresh")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.pushButton.setText(_translate("Dialog", "Close"))
        self.label.setText(_translate("Dialog", "Lower"))
        self.label_2.setText(_translate("Dialog", "Higher"))
        self.pB_copy_for_all.setText(_translate("Dialog", "set current parameters to all"))

