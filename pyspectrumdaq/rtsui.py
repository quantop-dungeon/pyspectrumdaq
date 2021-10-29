# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'rts.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_RtsWidget(object):
    def setupUi(self, RtsWidget):
        RtsWidget.setObjectName("RtsWidget")
        RtsWidget.resize(1149, 767)
        RtsWidget.setStyleSheet("QWidget {\n"
"    font: 8pt \"Open Sans\";\n"
"    background-color: white;\n"
"}\n"
"QLabel {\n"
"    padding: 1px 3px 1px 3px; /*top right bottom left*/\n"
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
"    background-color: rgb(245, 245, 245);\n"
"}\n"
"QPushButton { \n"
"    background-color: rgb(255, 255, 255);\n"
"    border-style: solid;\n"
"    border-width: 1px;\n"
"    border-radius: 5px;\n"
"    border-color: rgb(0, 0, 0);\n"
"    padding: 3px; \n"
"    min-width: 70;\n"
"}")
        self.verticalLayout = QtWidgets.QVBoxLayout(RtsWidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.gridLayout_3 = QtWidgets.QGridLayout()
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.spectrumPlot = PlotWidget(RtsWidget)
        self.spectrumPlot.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)
        self.spectrumPlot.setObjectName("spectrumPlot")
        self.gridLayout_3.addWidget(self.spectrumPlot, 0, 0, 1, 1)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.basedirLabel = QtWidgets.QLabel(RtsWidget)
        self.basedirLabel.setObjectName("basedirLabel")
        self.horizontalLayout.addWidget(self.basedirLabel, 0, QtCore.Qt.AlignRight)
        self.basedirLineEdit = QtWidgets.QLineEdit(RtsWidget)
        self.basedirLineEdit.setObjectName("basedirLineEdit")
        self.horizontalLayout.addWidget(self.basedirLineEdit)
        self.label_6 = QtWidgets.QLabel(RtsWidget)
        self.label_6.setMinimumSize(QtCore.QSize(100, 0))
        self.label_6.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_6.setObjectName("label_6")
        self.horizontalLayout.addWidget(self.label_6)
        self.fileFormatComboBox = QtWidgets.QComboBox(RtsWidget)
        self.fileFormatComboBox.setMinimumSize(QtCore.QSize(70, 0))
        self.fileFormatComboBox.setObjectName("fileFormatComboBox")
        self.fileFormatComboBox.addItem("")
        self.fileFormatComboBox.addItem("")
        self.horizontalLayout.addWidget(self.fileFormatComboBox)
        self.gridLayout_3.addLayout(self.horizontalLayout, 4, 0, 1, 1)
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
        self.label_2 = QtWidgets.QLabel(self.widget)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 11, 0, 1, 1, QtCore.Qt.AlignRight)
        self.samplerateLineEdit = QtWidgets.QLineEdit(self.widget)
        self.samplerateLineEdit.setMaximumSize(QtCore.QSize(100, 16777215))
        self.samplerateLineEdit.setObjectName("samplerateLineEdit")
        self.gridLayout.addWidget(self.samplerateLineEdit, 1, 1, 1, 1)
        self.samplerateLabel = QtWidgets.QLabel(self.widget)
        self.samplerateLabel.setObjectName("samplerateLabel")
        self.gridLayout.addWidget(self.samplerateLabel, 1, 0, 1, 1, QtCore.Qt.AlignRight)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem1, 10, 1, 1, 1)
        self.terminationComboBox = QtWidgets.QComboBox(self.widget)
        self.terminationComboBox.setObjectName("terminationComboBox")
        self.terminationComboBox.addItem("")
        self.terminationComboBox.addItem("")
        self.gridLayout.addWidget(self.terminationComboBox, 6, 1, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.widget)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 12, 0, 1, 1, QtCore.Qt.AlignRight)
        self.averagesCompletedLabel = QtWidgets.QLabel(self.widget)
        self.averagesCompletedLabel.setObjectName("averagesCompletedLabel")
        self.gridLayout.addWidget(self.averagesCompletedLabel, 12, 1, 1, 1)
        self.label_5 = QtWidgets.QLabel(self.widget)
        self.label_5.setObjectName("label_5")
        self.gridLayout.addWidget(self.label_5, 4, 0, 1, 1, QtCore.Qt.AlignRight)
        self.trigmodeComboBox = QtWidgets.QComboBox(self.widget)
        self.trigmodeComboBox.setMaximumSize(QtCore.QSize(100, 16777215))
        self.trigmodeComboBox.setObjectName("trigmodeComboBox")
        self.trigmodeComboBox.addItem("")
        self.trigmodeComboBox.addItem("")
        self.gridLayout.addWidget(self.trigmodeComboBox, 9, 1, 1, 1)
        self.terminationLabel = QtWidgets.QLabel(self.widget)
        self.terminationLabel.setObjectName("terminationLabel")
        self.gridLayout.addWidget(self.terminationLabel, 6, 0, 1, 1, QtCore.Qt.AlignRight)
        self.traceListWidget = QtWidgets.QListWidget(self.widget)
        self.traceListWidget.setObjectName("traceListWidget")
        item = QtWidgets.QListWidgetItem()
        self.traceListWidget.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.traceListWidget.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.traceListWidget.addItem(item)
        self.gridLayout.addWidget(self.traceListWidget, 14, 0, 1, 2)
        self.rbwLabel = QtWidgets.QLabel(self.widget)
        self.rbwLabel.setObjectName("rbwLabel")
        self.gridLayout.addWidget(self.rbwLabel, 4, 1, 1, 1)
        self.averagePushButton = QtWidgets.QPushButton(self.widget)
        self.averagePushButton.setObjectName("averagePushButton")
        self.gridLayout.addWidget(self.averagePushButton, 13, 1, 1, 1)
        spacerItem2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem2, 8, 1, 1, 1)
        self.label = QtWidgets.QLabel(self.widget)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 9, 0, 1, 1, QtCore.Qt.AlignRight)
        self.navgrtLineEdit = QtWidgets.QLineEdit(self.widget)
        self.navgrtLineEdit.setObjectName("navgrtLineEdit")
        self.gridLayout.addWidget(self.navgrtLineEdit, 16, 1, 1, 1)
        self.label_4 = QtWidgets.QLabel(self.widget)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 16, 0, 1, 1, QtCore.Qt.AlignRight)
        self.channelLabel = QtWidgets.QLabel(self.widget)
        self.channelLabel.setObjectName("channelLabel")
        self.gridLayout.addWidget(self.channelLabel, 5, 0, 1, 1, QtCore.Qt.AlignRight)
        self.channelComboBox = QtWidgets.QComboBox(self.widget)
        self.channelComboBox.setMinimumSize(QtCore.QSize(0, 0))
        self.channelComboBox.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.channelComboBox.setObjectName("channelComboBox")
        self.channelComboBox.addItem("")
        self.channelComboBox.addItem("")
        self.channelComboBox.addItem("")
        self.channelComboBox.addItem("")
        self.gridLayout.addWidget(self.channelComboBox, 5, 1, 1, 1)
        self.nsamplesComboBox = QtWidgets.QComboBox(self.widget)
        self.nsamplesComboBox.setObjectName("nsamplesComboBox")
        self.nsamplesComboBox.addItem("")
        self.nsamplesComboBox.addItem("")
        self.nsamplesComboBox.addItem("")
        self.gridLayout.addWidget(self.nsamplesComboBox, 2, 1, 1, 1)
        self.fullrangeLabel = QtWidgets.QLabel(self.widget)
        self.fullrangeLabel.setObjectName("fullrangeLabel")
        self.gridLayout.addWidget(self.fullrangeLabel, 7, 0, 1, 1, QtCore.Qt.AlignRight)
        self.fullrangeComboBox = QtWidgets.QComboBox(self.widget)
        self.fullrangeComboBox.setObjectName("fullrangeComboBox")
        self.fullrangeComboBox.addItem("")
        self.fullrangeComboBox.addItem("")
        self.fullrangeComboBox.addItem("")
        self.fullrangeComboBox.addItem("")
        self.fullrangeComboBox.addItem("")
        self.fullrangeComboBox.addItem("")
        self.gridLayout.addWidget(self.fullrangeComboBox, 7, 1, 1, 1)
        self.naveragesLineEdit = QtWidgets.QLineEdit(self.widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.naveragesLineEdit.sizePolicy().hasHeightForWidth())
        self.naveragesLineEdit.setSizePolicy(sizePolicy)
        self.naveragesLineEdit.setMaximumSize(QtCore.QSize(100, 16777215))
        self.naveragesLineEdit.setObjectName("naveragesLineEdit")
        self.gridLayout.addWidget(self.naveragesLineEdit, 11, 1, 1, 1)
        self.nsamplesLabel = QtWidgets.QLabel(self.widget)
        self.nsamplesLabel.setObjectName("nsamplesLabel")
        self.gridLayout.addWidget(self.nsamplesLabel, 2, 0, 1, 1, QtCore.Qt.AlignRight)
        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)
        self.scopePlot = PlotWidget(self.widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.scopePlot.sizePolicy().hasHeightForWidth())
        self.scopePlot.setSizePolicy(sizePolicy)
        self.scopePlot.setMinimumSize(QtCore.QSize(0, 200))
        self.scopePlot.setMaximumSize(QtCore.QSize(16777215, 200))
        self.scopePlot.setObjectName("scopePlot")
        self.gridLayout_2.addWidget(self.scopePlot, 7, 0, 1, 1)
        self.gridLayout_3.addWidget(self.widget, 0, 1, 5, 1)
        self.verticalLayout.addLayout(self.gridLayout_3)

        self.retranslateUi(RtsWidget)
        QtCore.QMetaObject.connectSlotsByName(RtsWidget)

    def retranslateUi(self, RtsWidget):
        _translate = QtCore.QCoreApplication.translate
        RtsWidget.setWindowTitle(_translate("RtsWidget", "Form"))
        self.basedirLabel.setText(_translate("RtsWidget", "Base directory"))
        self.label_6.setText(_translate("RtsWidget", "File format"))
        self.fileFormatComboBox.setItemText(0, _translate("RtsWidget", "hdf5"))
        self.fileFormatComboBox.setItemText(1, _translate("RtsWidget", "txt"))
        self.label_2.setText(_translate("RtsWidget", "N averages"))
        self.samplerateLineEdit.setText(_translate("RtsWidget", "30e6"))
        self.samplerateLabel.setText(_translate("RtsWidget", "Sampling rate (Hz)"))
        self.terminationComboBox.setItemText(0, _translate("RtsWidget", "1 MOhm"))
        self.terminationComboBox.setItemText(1, _translate("RtsWidget", "50 Ohm"))
        self.label_3.setText(_translate("RtsWidget", "Completed"))
        self.averagesCompletedLabel.setText(_translate("RtsWidget", "0"))
        self.label_5.setText(_translate("RtsWidget", "RBW (Hz)"))
        self.trigmodeComboBox.setItemText(0, _translate("RtsWidget", "Software"))
        self.trigmodeComboBox.setItemText(1, _translate("RtsWidget", "External"))
        self.terminationLabel.setText(_translate("RtsWidget", "Termination"))
        self.traceListWidget.setToolTip(_translate("RtsWidget", "<html><head/><body><p>Ctr+s - save selected</p><p>Ctrl+x - hide/show trace </p><p>Del - delete selected</p></body></html>"))
        __sortingEnabled = self.traceListWidget.isSortingEnabled()
        self.traceListWidget.setSortingEnabled(False)
        item = self.traceListWidget.item(0)
        item.setText(_translate("RtsWidget", "Trace 1"))
        item = self.traceListWidget.item(1)
        item.setText(_translate("RtsWidget", "Background"))
        item = self.traceListWidget.item(2)
        item.setText(_translate("RtsWidget", "Background without input"))
        self.traceListWidget.setSortingEnabled(__sortingEnabled)
        self.rbwLabel.setText(_translate("RtsWidget", "700"))
        self.averagePushButton.setText(_translate("RtsWidget", "Average"))
        self.label.setText(_translate("RtsWidget", "Trigger"))
        self.navgrtLineEdit.setToolTip(_translate("RtsWidget", "<html><head/><body><p>The number of averages for the real-time trace.</p></body></html>"))
        self.navgrtLineEdit.setWhatsThis(_translate("RtsWidget", "<html><head/><body><p><br/></p></body></html>"))
        self.navgrtLineEdit.setText(_translate("RtsWidget", "1"))
        self.label_4.setText(_translate("RtsWidget", "Display averages"))
        self.channelLabel.setText(_translate("RtsWidget", "Channel"))
        self.channelComboBox.setItemText(0, _translate("RtsWidget", "0"))
        self.channelComboBox.setItemText(1, _translate("RtsWidget", "1"))
        self.channelComboBox.setItemText(2, _translate("RtsWidget", "2"))
        self.channelComboBox.setItemText(3, _translate("RtsWidget", "3"))
        self.nsamplesComboBox.setItemText(0, _translate("RtsWidget", "2,048"))
        self.nsamplesComboBox.setItemText(1, _translate("RtsWidget", "4,096"))
        self.nsamplesComboBox.setItemText(2, _translate("RtsWidget", "8,192"))
        self.fullrangeLabel.setText(_translate("RtsWidget", "Full range (V)"))
        self.fullrangeComboBox.setItemText(0, _translate("RtsWidget", "0.2"))
        self.fullrangeComboBox.setItemText(1, _translate("RtsWidget", "0.5"))
        self.fullrangeComboBox.setItemText(2, _translate("RtsWidget", "1"))
        self.fullrangeComboBox.setItemText(3, _translate("RtsWidget", "2"))
        self.fullrangeComboBox.setItemText(4, _translate("RtsWidget", "5"))
        self.fullrangeComboBox.setItemText(5, _translate("RtsWidget", "10"))
        self.naveragesLineEdit.setText(_translate("RtsWidget", "100"))
        self.nsamplesLabel.setText(_translate("RtsWidget", "N samples"))
from pyqtgraph import PlotWidget
