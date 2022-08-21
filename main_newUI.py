import sys
from PyQt5.QtWidgets import QApplication,QPushButton, QMainWindow, \
    QAction, QInputDialog, QDesktopWidget, QFileDialog
from editLabel import EditLabel
from analyzeLabel import AnalyzeLabel
from pyqtDesign.pyqtDesigner import Ui_MainWindow

import glob, json, os
import numpy as np

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.pathInit()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        #self.setWindowTitle("json파일 편집 프로그램")
        self.statusBarMessage()
        #self.centerWindow()
        self.mainWindow()

    def pathInit(self, inputPath = None):
        self.resultPath = None
        self.clipPath = None
        self.upperPath = None

        if inputPath:
            basePath = os.path.basename(inputPath)

            if basePath == 'result':
                self.resultPath = inputPath
                self.clipPath = os.path.dirname(inputPath)
                self.upperPath = os.path.dirname(self.clipPath)

    def centerWindow(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def statusBarMessage(self, message = None):
        self.statusBar().showMessage("경로를 설정해주세요")
        self.printText("경로를 설정해주세요")

        if message:
            self.statusBar().showMessage(message)
            self.printText(message)
        # else:
        #     self.statusBar().showMessage('잘못된 입력입니다.')
        #     print('잘못된 입력입니다.')
    
    def printText(self, text = None):
        self.ui.textBrowser.append(text)
        print(text)


    def mainWindow(self):
        pass

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec_())