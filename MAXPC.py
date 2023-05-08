from types import NoneType
import typing
from PyQt5 import QtCore, QtWidgets, QtPrintSupport, uic
import sys
import sqlite3
from PyQt5.QtWidgets import QWidget
from PyQt5.uic import loadUi
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPixmap
from datetime import datetime
import easygui as eg
import random
import re
import time

class Main_Program(QtWidgets.QMainWindow):
    def __init__(self):
        super(Main_Program, self).__init__()
        uic.loadUi('main.ui', self)

class LogIn (QSplashScreen):
    def __init__(self):
        super(LogIn, self).__init__()
        uic.loadUi('login.ui', self)
        self.closeSplash()
        self.main = Main_Program()
        self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)
        pixmap = QPixmap("SplashBG.png")
        pixmap = pixmap.scaled(850, 850, Qt.KeepAspectRatio)
        self.setPixmap(pixmap)
        self.btnLogIn.clicked.connect(lambda: self.check_login())
        self.btnCancel.clicked.connect(lambda: self.closeSplash())

    def check_login(self):
        username = self.txtUsername.text()
        password = self.txtPassword.text()
        if username == "admin" and password == "admin":
            self.close()
            self.main.show()
        else:
            dialog = QMessageBox.warning(self, 'Error', "Bobo ka tanga", QMessageBox.Ok)

    def closeSplash(self):
        self.close()

    def mousePressEvent(self, event):
    # disable default "click-to-dismiss" behaviour
        pass



app = QtWidgets.QApplication(sys.argv)
splash = LogIn()
splash.show()
app.exec_()