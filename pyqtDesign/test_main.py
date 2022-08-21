from PyQt5.QtWidgets import QApplication,QPushButton, QMainWindow, \
    QAction, QInputDialog, QDesktopWidget, QFileDialog, QComboBox
from PyQt5 import QtCore, QtGui, QtWidgets
from pyqtDesigner import Ui_MainWindow

import sys, os
import re, numpy as np

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.filepath = None
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.comboboxInit()
        self.statusBarMessage()
        self.mainWindowEvent()
        self.count = 1

    # 메인 윈도우 이벤트
    def mainWindowEvent(self):
        self.ui.comboboxPushButton.clicked.connect(self.comboboxButton)

    # 콤보박스 내용 사전으로 초기화
    def comboboxInit(self):
        self.comboboxText = {}
        # combobox text list
        for i in range(len(self.ui.comboBox)):
            self.comboboxText[self.ui.comboBox.itemText(i)] = i

    # 콤보박스 선택 후 버튼 클릭 이벤트
    def comboboxButton(self):
        # 콤보박스의 선택된 
        curComboText = self.ui.comboBox.currentText()
        
        if curComboText in self.comboboxText:
            print(curComboText, ':', self.comboboxText[curComboText])
        
            

    # 윈도우를 화면 가운데에 팝업
    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def statusBarMessage(self, message = None):
        if message:
            self.statusBar().showMessage(message)
        else:
            self.statusBar().showMessage('경로를 설정해주세요')
            print('경로를 설정해주세요')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec_())