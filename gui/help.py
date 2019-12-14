# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'help.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.setWindowModality(QtCore.Qt.ApplicationModal)
        Dialog.resize(411, 251)
        Dialog.setMinimumSize(QtCore.QSize(411, 251))
        Dialog.setMaximumSize(QtCore.QSize(411, 251))
        Dialog.setModal(True)
        self.tabWidget = QtWidgets.QTabWidget(Dialog)
        self.tabWidget.setGeometry(QtCore.QRect(10, 10, 391, 201))
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.label = QtWidgets.QLabel(self.tab)
        self.label.setGeometry(QtCore.QRect(10, 10, 361, 121))
        self.label.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.label.setWordWrap(True)
        self.label.setObjectName("label")
        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.label_2 = QtWidgets.QLabel(self.tab_2)
        self.label_2.setGeometry(QtCore.QRect(10, 10, 361, 161))
        self.label_2.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.label_2.setWordWrap(True)
        self.label_2.setObjectName("label_2")
        self.tabWidget.addTab(self.tab_2, "")
        self.pushButton = QtWidgets.QPushButton(Dialog)
        self.pushButton.setGeometry(QtCore.QRect(270, 220, 111, 23))
        self.pushButton.setObjectName("pushButton")

        self.retranslateUi(Dialog)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Help"))
        self.label.setText(_translate("Dialog", "For an InfoReq message, you can choose to either request a METAR, short TAF, TAF or VATSIM ATIS text from VATSIM for the airport supplied in the \"Airport\" field as an ICAO code. If you request a METAR or either type of TAF, data is pulled from NOAA by Hoppie then relayed back to you. If you choose a VATSIM ATIS, Hoppie will take the ATIS text from VATSIM if there is a controller online and broadcasting an ATIS for that airport. If not, a message is returned saying \"not available\"."))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("Dialog", "InfoReq"))
        self.label_2.setText(_translate("Dialog", "When sending a CPDLC message, you need to specify what response is expected from the other party.\n"
"\"Yes\" and \"No\" are the only ones specified by an airplane, which are used to specify if they require a response from ATC. The rest are usually used by ATC to specify what response they require from the airplane. This response should be placed in the message box.\n"
"If you check the \"response\" box, you will be asked for the message ID that you are responding to. This can be found in the message content, using the plan below:\n"
"\n"
"/data2/{message ID of this message}/{message ID which this is responding to (can be ommitted)}/{response type required}/{message content}"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("Dialog", "CPDLC"))
        self.pushButton.setText(_translate("Dialog", "Close"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())
