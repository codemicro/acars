# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'about.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.setWindowModality(QtCore.Qt.ApplicationModal)
        Dialog.resize(400, 110)
        Dialog.setMinimumSize(QtCore.QSize(400, 110))
        Dialog.setMaximumSize(QtCore.QSize(400, 110))
        Dialog.setModal(True)
        self.versionLabel = QtWidgets.QLabel(Dialog)
        self.versionLabel.setGeometry(QtCore.QRect(110, 40, 261, 21))
        self.versionLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.versionLabel.setObjectName("versionLabel")
        self.imageWidget = QtWidgets.QWidget(Dialog)
        self.imageWidget.setGeometry(QtCore.QRect(20, 10, 90, 90))
        self.imageWidget.setObjectName("imageWidget")
        self.mainLabel = QtWidgets.QLabel(Dialog)
        self.mainLabel.setGeometry(QtCore.QRect(100, 20, 281, 21))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.mainLabel.setFont(font)
        self.mainLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.mainLabel.setObjectName("mainLabel")
        self.madeLabel = QtWidgets.QLabel(Dialog)
        self.madeLabel.setGeometry(QtCore.QRect(110, 56, 261, 20))
        self.madeLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.madeLabel.setObjectName("madeLabel")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "About"))
        self.versionLabel.setText(_translate("Dialog", "Version 0.1.0 alpha released... not yet"))
        self.mainLabel.setText(_translate("Dialog", "ACARS by Tom Pain"))
        self.madeLabel.setText(_translate("Dialog", "Made 2019"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())
