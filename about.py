# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'about.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(400, 111)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Form.sizePolicy().hasHeightForWidth())
        Form.setSizePolicy(sizePolicy)
        Form.setMinimumSize(QtCore.QSize(0, 0))
        Form.setMaximumSize(QtCore.QSize(1000, 1000))
        self.mainLabel = QtWidgets.QLabel(Form)
        self.mainLabel.setGeometry(QtCore.QRect(110, 20, 281, 21))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.mainLabel.setFont(font)
        self.mainLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.mainLabel.setObjectName("mainLabel")
        self.versionLabel = QtWidgets.QLabel(Form)
        self.versionLabel.setGeometry(QtCore.QRect(120, 40, 261, 21))
        self.versionLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.versionLabel.setObjectName("versionLabel")
        self.madeLabel = QtWidgets.QLabel(Form)
        self.madeLabel.setGeometry(QtCore.QRect(120, 56, 261, 20))
        self.madeLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.madeLabel.setObjectName("madeLabel")
        self.imageWidget = QtWidgets.QWidget(Form)
        self.imageWidget.setGeometry(QtCore.QRect(30, 10, 90, 90))
        self.imageWidget.setObjectName("imageWidget")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "About"))
        self.mainLabel.setText(_translate("Form", "ACARS by Tom Pain"))
        self.versionLabel.setText(_translate("Form", "Version 0.1.0 alpha released... not yet"))
        self.madeLabel.setText(_translate("Form", "Made 2019"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())
