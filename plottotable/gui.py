# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainwindow.ui'
#
# Created: Wed Mar 16 04:02:20 2016
#      by: PyQt4 UI code generator 4.10.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8

    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(896, 743)
        self.centralWidget = QtGui.QWidget(MainWindow)
        self.centralWidget.setObjectName(_fromUtf8("centralWidget"))
        self.horizontalLayout_4 = QtGui.QHBoxLayout(self.centralWidget)
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.widget_2 = QtGui.QWidget(self.centralWidget)
        self.widget_2.setMinimumSize(QtCore.QSize(291, 0))
        self.widget_2.setMaximumSize(QtCore.QSize(291, 16777215))
        self.widget_2.setObjectName(_fromUtf8("widget_2"))
        self.verticalLayout = QtGui.QVBoxLayout(self.widget_2)
        self.verticalLayout.setMargin(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.pic_area = QtGui.QScrollArea(self.widget_2)
        self.pic_area.setMinimumSize(QtCore.QSize(269, 504))
        self.pic_area.setMaximumSize(QtCore.QSize(269, 16777215))
        self.pic_area.setAutoFillBackground(True)
        self.pic_area.setWidgetResizable(True)
        self.pic_area.setObjectName(_fromUtf8("pic_area"))
        self.scrollAreaWidgetContents = QtGui.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 267, 629))
        self.scrollAreaWidgetContents.setObjectName(_fromUtf8("scrollAreaWidgetContents"))
        self.pic_area.setWidget(self.scrollAreaWidgetContents)
        self.verticalLayout.addWidget(self.pic_area)
        self.horizontalLayout_4.addWidget(self.widget_2)
        self.widget_3 = QtGui.QWidget(self.centralWidget)
        self.widget_3.setObjectName(_fromUtf8("widget_3"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.widget_3)
        self.verticalLayout_2.setMargin(0)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.widget_4 = QtGui.QWidget(self.widget_3)
        self.widget_4.setMinimumSize(QtCore.QSize(0, 50))
        self.widget_4.setMaximumSize(QtCore.QSize(520, 35))
        self.widget_4.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.widget_4.setObjectName(_fromUtf8("widget_4"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.widget_4)
        self.horizontalLayout.setMargin(0)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.print_btn = QtGui.QPushButton(self.widget_4)
        self.print_btn.setMinimumSize(QtCore.QSize(115, 31))
        self.print_btn.setMaximumSize(QtCore.QSize(115, 31))
        self.print_btn.setObjectName(_fromUtf8("print_btn"))
        self.horizontalLayout.addWidget(self.print_btn)
        self.save_btn = QtGui.QToolButton(self.widget_4)
        self.save_btn.setMinimumSize(QtCore.QSize(115, 31))
        self.save_btn.setMaximumSize(QtCore.QSize(115, 31))
        self.save_btn.setObjectName(_fromUtf8("save_btn"))
        self.horizontalLayout.addWidget(self.save_btn)
        self.plot_btn = QtGui.QPushButton(self.widget_4)
        self.plot_btn.setMinimumSize(QtCore.QSize(115, 31))
        self.plot_btn.setMaximumSize(QtCore.QSize(115, 31))
        self.plot_btn.setObjectName(_fromUtf8("plot_btn"))
        self.horizontalLayout.addWidget(self.plot_btn)
        self.open_btn = QtGui.QPushButton(self.widget_4)
        self.open_btn.setMinimumSize(QtCore.QSize(115, 31))
        self.open_btn.setMaximumSize(QtCore.QSize(115, 31))
        self.open_btn.setObjectName(_fromUtf8("open_btn"))
        self.horizontalLayout.addWidget(self.open_btn)
        self.verticalLayout_2.addWidget(self.widget_4)
        self.widget = QtGui.QWidget(self.widget_3)
        self.widget.setObjectName(_fromUtf8("widget"))
        self.horizontalLayout_3 = QtGui.QHBoxLayout(self.widget)
        self.horizontalLayout_3.setMargin(0)
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.pic_hold = QtGui.QScrollArea(self.widget)
        self.pic_hold.setMinimumSize(QtCore.QSize(532, 542))
        self.pic_hold.setWidgetResizable(True)
        self.pic_hold.setObjectName(_fromUtf8("pic_hold"))
        self.scrollAreaWidgetContents_2 = QtGui.QWidget()
        self.scrollAreaWidgetContents_2.setGeometry(QtCore.QRect(0, 0, 530, 550))
        self.scrollAreaWidgetContents_2.setObjectName(_fromUtf8("scrollAreaWidgetContents_2"))
        self.pic_hold.setWidget(self.scrollAreaWidgetContents_2)
        self.horizontalLayout_3.addWidget(self.pic_hold)
        self.verticalLayout_2.addWidget(self.widget)
        self.horizontalLayout_4.addWidget(self.widget_3)
        MainWindow.setCentralWidget(self.centralWidget)
        self.menuBar = QtGui.QMenuBar(MainWindow)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 896, 29))
        self.menuBar.setObjectName(_fromUtf8("menuBar"))
        self.menuFile = QtGui.QMenu(self.menuBar)
        self.menuFile.setObjectName(_fromUtf8("menuFile"))
        self.menuHelp = QtGui.QMenu(self.menuBar)
        self.menuHelp.setObjectName(_fromUtf8("menuHelp"))
        MainWindow.setMenuBar(self.menuBar)
        self.mainToolBar = QtGui.QToolBar(MainWindow)
        self.mainToolBar.setObjectName(_fromUtf8("mainToolBar"))
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.mainToolBar)
        self.statusBar = QtGui.QStatusBar(MainWindow)
        self.statusBar.setObjectName(_fromUtf8("statusBar"))
        MainWindow.setStatusBar(self.statusBar)
        self.actionOpen = QtGui.QAction(MainWindow)
        self.actionOpen.setObjectName(_fromUtf8("actionOpen"))
        self.actionPlot = QtGui.QAction(MainWindow)
        self.actionPlot.setObjectName(_fromUtf8("actionPlot"))
        self.actionSave = QtGui.QAction(MainWindow)
        self.actionSave.setObjectName(_fromUtf8("actionSave"))
        self.actionPrint = QtGui.QAction(MainWindow)
        self.actionPrint.setObjectName(_fromUtf8("actionPrint"))
        self.actionusermanual = QtGui.QAction(MainWindow)
        self.actionusermanual.setObjectName(_fromUtf8("actionusermanual"))
        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionPlot)
        self.menuFile.addAction(self.actionSave)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionPrint)
        self.menuHelp.addAction(self.actionusermanual)
        self.menuBar.addAction(self.menuFile.menuAction())
        self.menuBar.addAction(self.menuHelp.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow", None))
        self.print_btn.setText(_translate("MainWindow", "Print", None))
        self.save_btn.setText(_translate("MainWindow", "Save", None))
        self.plot_btn.setText(_translate("MainWindow", "Plot", None))
        self.open_btn.setText(_translate("MainWindow", "Open", None))
        self.menuFile.setTitle(_translate("MainWindow", "File", None))
        self.menuHelp.setTitle(_translate("MainWindow", "Help", None))
        self.actionOpen.setText(_translate("MainWindow", "Open", None))
        self.actionPlot.setText(_translate("MainWindow", "Plot", None))
        self.actionSave.setText(_translate("MainWindow", "Save", None))
        self.actionPrint.setText(_translate("MainWindow", "Print", None))
        self.actionusermanual.setText(_translate("MainWindow", "User Manual", None))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    MainWindow = QtGui.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

