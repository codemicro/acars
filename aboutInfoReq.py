# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'aboutInfoReq.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_AboutInfoReq(object):
    def setupUi(self, AboutInfoReq):
        AboutInfoReq.setObjectName("AboutInfoReq")
        AboutInfoReq.resize(400, 141)
        AboutInfoReq.setMinimumSize(QtCore.QSize(400, 141))
        AboutInfoReq.setMaximumSize(QtCore.QSize(400, 141))
        self.label = QtWidgets.QLabel(AboutInfoReq)
        self.label.setGeometry(QtCore.QRect(10, 10, 381, 281))
        self.label.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.label.setWordWrap(True)
        self.label.setObjectName("label")
        self.pushButton = QtWidgets.QPushButton(AboutInfoReq)
        self.pushButton.setGeometry(QtCore.QRect(274, 110, 111, 23))
        self.pushButton.setObjectName("pushButton")

        self.retranslateUi(AboutInfoReq)
        QtCore.QMetaObject.connectSlotsByName(AboutInfoReq)

    def retranslateUi(self, AboutInfoReq):
        _translate = QtCore.QCoreApplication.translate
        AboutInfoReq.setWindowTitle(_translate("AboutInfoReq", "About InfoReq"))
        self.label.setText(_translate("AboutInfoReq", "For an InfoReq message, you can choose to either request a METAR, short TAF, TAF or VATSIM ATIS text from VATSIM for the airport supplied in the \"Airport\" field as an ICAO code. If you request a METAR or either type of TAF, data is pulled from NOAA by Hoppie then relayed back to you. If you choose a VATSIM ATIS, Hoppie will take the ATIS text from VATSIM if there is a controller online and broadcasting an ATIS for that airport. If not, a message is returned saying \"not available\"."))
        self.pushButton.setText(_translate("AboutInfoReq", "Close"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    AboutInfoReq = QtWidgets.QWidget()
    ui = Ui_AboutInfoReq()
    ui.setupUi(AboutInfoReq)
    AboutInfoReq.show()
    sys.exit(app.exec_())
