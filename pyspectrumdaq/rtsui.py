# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'rts.ui'
#
# Created by: PyQt5 UI code generator 5.12.3
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_RtsWidget(object):
    def setupUi(self, RtsWidget):
        RtsWidget.setObjectName("RtsWidget")
        RtsWidget.resize(1149, 679)
        RtsWidget.setStyleSheet("QWidget {\n"
"    font: 8pt \"Open Sans\";\n"
"    background-color: white;\n"
"}\n"
"QLineEdit {\n"
"    padding: 1px 3px 1px 3px; /*top right bottom left*/\n"
"}\n"
"QComboBox {\n"
"    border-style: solid;\n"
"    border-width: 1px;\n"
"    border-radius: 5px;\n"
"    border-color: rgb(0, 0, 0);\n"
"    padding: 1px 3px 1px 3px;\n"
"}\n"
"QComboBox:on { /* shift the text when the popup opens */\n"
"    border-bottom-right-radius: 0px;\n"
"    border-bottom-left-radius: 0px;\n"
"}\n"
"QComboBox::drop-down {\n"
"    border-left-width: 1px;\n"
"    border-left-color: darkgray;\n"
"    border-left-style: solid; /*a single line */\n"
"    border-top-right-radius: 5px;\n"
"    border-bottom-right-radius: 5px;\n"
"}\n"
"QComboBox QAbstractItemView {\n"
"    background-color: rgb(240, 240, 240);\n"
"}\n"
"QPushButton { \n"
"    background-color: rgb(255, 255, 255);\n"
"    border-style: solid;\n"
"    border-width: 1px;\n"
"    border-radius: 5px;\n"
"    border-color: rgb(0, 0, 0);\n"
"    padding: 3px; \n"
"}")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(RtsWidget)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.plotWidget = PlotWidget(RtsWidget)
        self.plotWidget.setObjectName("plotWidget")
        self.horizontalLayout.addWidget(self.plotWidget)
        self.widget = QtWidgets.QWidget(RtsWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.widget.sizePolicy().hasHeightForWidth())
        self.widget.setSizePolicy(sizePolicy)
        self.widget.setMinimumSize(QtCore.QSize(200, 0))
        self.widget.setMaximumSize(QtCore.QSize(250, 16777215))
        self.widget.setObjectName("widget")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.widget)
        self.gridLayout_2.setObjectName("gridLayout_2")
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_2.addItem(spacerItem, 6, 0, 1, 1)
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        self.gridLayout.setObjectName("gridLayout")
        self.nsamplesLineEdit = QtWidgets.QLineEdit(self.widget)
        self.nsamplesLineEdit.setMaximumSize(QtCore.QSize(100, 16777215))
        self.nsamplesLineEdit.setObjectName("nsamplesLineEdit")
        self.gridLayout.addWidget(self.nsamplesLineEdit, 2, 1, 1, 1)
        self.fullrangeLabel = QtWidgets.QLabel(self.widget)
        self.fullrangeLabel.setObjectName("fullrangeLabel")
        self.gridLayout.addWidget(self.fullrangeLabel, 5, 0, 1, 1, QtCore.Qt.AlignRight)
        self.label_2 = QtWidgets.QLabel(self.widget)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 9, 0, 1, 1, QtCore.Qt.AlignRight)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem1, 8, 1, 1, 1)
        self.terminationLabel = QtWidgets.QLabel(self.widget)
        self.terminationLabel.setObjectName("terminationLabel")
        self.gridLayout.addWidget(self.terminationLabel, 4, 0, 1, 1, QtCore.Qt.AlignRight)
        self.channelComboBox = QtWidgets.QComboBox(self.widget)
        self.channelComboBox.setMinimumSize(QtCore.QSize(0, 0))
        self.channelComboBox.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.channelComboBox.setObjectName("channelComboBox")
        self.channelComboBox.addItem("")
        self.channelComboBox.addItem("")
        self.channelComboBox.addItem("")
        self.channelComboBox.addItem("")
        self.gridLayout.addWidget(self.channelComboBox, 3, 1, 1, 1)
        self.fullrangeComboBox = QtWidgets.QComboBox(self.widget)
        self.fullrangeComboBox.setObjectName("fullrangeComboBox")
        self.fullrangeComboBox.addItem("")
        self.fullrangeComboBox.addItem("")
        self.fullrangeComboBox.addItem("")
        self.fullrangeComboBox.addItem("")
        self.fullrangeComboBox.addItem("")
        self.fullrangeComboBox.addItem("")
        self.gridLayout.addWidget(self.fullrangeComboBox, 5, 1, 1, 1)
        self.samplerateLineEdit = QtWidgets.QLineEdit(self.widget)
        self.samplerateLineEdit.setMaximumSize(QtCore.QSize(100, 16777215))
        self.samplerateLineEdit.setObjectName("samplerateLineEdit")
        self.gridLayout.addWidget(self.samplerateLineEdit, 1, 1, 1, 1)
        self.naveragesLineEdit = QtWidgets.QLineEdit(self.widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.naveragesLineEdit.sizePolicy().hasHeightForWidth())
        self.naveragesLineEdit.setSizePolicy(sizePolicy)
        self.naveragesLineEdit.setMaximumSize(QtCore.QSize(100, 16777215))
        self.naveragesLineEdit.setObjectName("naveragesLineEdit")
        self.gridLayout.addWidget(self.naveragesLineEdit, 9, 1, 1, 1)
        spacerItem2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem2, 6, 1, 1, 1)
        self.averagesCompletedLabel = QtWidgets.QLabel(self.widget)
        self.averagesCompletedLabel.setObjectName("averagesCompletedLabel")
        self.gridLayout.addWidget(self.averagesCompletedLabel, 10, 1, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.widget)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 10, 0, 1, 1, QtCore.Qt.AlignRight)
        self.terminationComboBox = QtWidgets.QComboBox(self.widget)
        self.terminationComboBox.setObjectName("terminationComboBox")
        self.terminationComboBox.addItem("")
        self.terminationComboBox.addItem("")
        self.gridLayout.addWidget(self.terminationComboBox, 4, 1, 1, 1)
        self.label = QtWidgets.QLabel(self.widget)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 7, 0, 1, 1, QtCore.Qt.AlignRight)
        self.channelLabel = QtWidgets.QLabel(self.widget)
        self.channelLabel.setObjectName("channelLabel")
        self.gridLayout.addWidget(self.channelLabel, 3, 0, 1, 1, QtCore.Qt.AlignRight)
        self.nsamplesLabel = QtWidgets.QLabel(self.widget)
        self.nsamplesLabel.setObjectName("nsamplesLabel")
        self.gridLayout.addWidget(self.nsamplesLabel, 2, 0, 1, 1, QtCore.Qt.AlignRight)
        self.samplerateLabel = QtWidgets.QLabel(self.widget)
        self.samplerateLabel.setObjectName("samplerateLabel")
        self.gridLayout.addWidget(self.samplerateLabel, 1, 0, 1, 1, QtCore.Qt.AlignRight)
        self.trigmodeComboBox = QtWidgets.QComboBox(self.widget)
        self.trigmodeComboBox.setMaximumSize(QtCore.QSize(100, 16777215))
        self.trigmodeComboBox.setObjectName("trigmodeComboBox")
        self.trigmodeComboBox.addItem("")
        self.trigmodeComboBox.addItem("")
        self.gridLayout.addWidget(self.trigmodeComboBox, 7, 1, 1, 1)
        self.averagePushButton = QtWidgets.QPushButton(self.widget)
        self.averagePushButton.setObjectName("averagePushButton")
        self.gridLayout.addWidget(self.averagePushButton, 11, 1, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)
        self.scopePlot = PlotWidget(self.widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.scopePlot.sizePolicy().hasHeightForWidth())
        self.scopePlot.setSizePolicy(sizePolicy)
        self.scopePlot.setMaximumSize(QtCore.QSize(16777215, 200))
        self.scopePlot.setObjectName("scopePlot")
        self.gridLayout_2.addWidget(self.scopePlot, 7, 0, 1, 1)
        self.horizontalLayout.addWidget(self.widget)
        self.horizontalLayout_2.addLayout(self.horizontalLayout)

        self.retranslateUi(RtsWidget)
        QtCore.QMetaObject.connectSlotsByName(RtsWidget)

    def retranslateUi(self, RtsWidget):
        _translate = QtCore.QCoreApplication.translate
        RtsWidget.setWindowTitle(_translate("RtsWidget", "Form"))
        self.nsamplesLineEdit.setText(_translate("RtsWidget", "409600"))
        self.fullrangeLabel.setText(_translate("RtsWidget", "Full range (V)"))
        self.label_2.setText(_translate("RtsWidget", "N averages"))
        self.terminationLabel.setText(_translate("RtsWidget", "Termination"))
        self.channelComboBox.setItemText(0, _translate("RtsWidget", "0"))
        self.channelComboBox.setItemText(1, _translate("RtsWidget", "1"))
        self.channelComboBox.setItemText(2, _translate("RtsWidget", "2"))
        self.channelComboBox.setItemText(3, _translate("RtsWidget", "3"))
        self.fullrangeComboBox.setItemText(0, _translate("RtsWidget", "0.2"))
        self.fullrangeComboBox.setItemText(1, _translate("RtsWidget", "0.5"))
        self.fullrangeComboBox.setItemText(2, _translate("RtsWidget", "1"))
        self.fullrangeComboBox.setItemText(3, _translate("RtsWidget", "2"))
        self.fullrangeComboBox.setItemText(4, _translate("RtsWidget", "5"))
        self.fullrangeComboBox.setItemText(5, _translate("RtsWidget", "10"))
        self.samplerateLineEdit.setText(_translate("RtsWidget", "30e6"))
        self.naveragesLineEdit.setText(_translate("RtsWidget", "100"))
        self.averagesCompletedLabel.setText(_translate("RtsWidget", "0"))
        self.label_3.setText(_translate("RtsWidget", "Completed"))
        self.terminationComboBox.setItemText(0, _translate("RtsWidget", "1 MOhm"))
        self.terminationComboBox.setItemText(1, _translate("RtsWidget", "50 Ohm"))
        self.label.setText(_translate("RtsWidget", "Trigger"))
        self.channelLabel.setText(_translate("RtsWidget", "Channel"))
        self.nsamplesLabel.setText(_translate("RtsWidget", "N samples"))
        self.samplerateLabel.setText(_translate("RtsWidget", "Sampling rate (Hz)"))
        self.trigmodeComboBox.setItemText(0, _translate("RtsWidget", "Software"))
        self.trigmodeComboBox.setItemText(1, _translate("RtsWidget", "External"))
        self.averagePushButton.setText(_translate("RtsWidget", "Average"))
from pyqtgraph import PlotWidget
