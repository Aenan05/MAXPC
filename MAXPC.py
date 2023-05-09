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
import random
import re
import time

class Main_Program(QtWidgets.QMainWindow):
    def __init__(self):
        super(Main_Program, self).__init__()
        uic.loadUi('main.ui', self)
        self.add = add()
        # self.edit = edit()
        self.restock = restock()
        self.checkout = CheckOut()
        self.records = records()
        self.view_logs = view_logs()
        self.btnAdd.clicked.connect (lambda: (self.add.show(), self.close(), self.add.lbladd_edit.setText('Add New Item'), self.add.display()))
        self.btnEdit.clicked.connect (lambda: (self.add.show(), self.close(), self.add.lbladd_edit.setText('Edit Item')))
        self.btnRestock.clicked.connect (lambda: (self.restock.show(), self.close()))
        self.btnCustR.clicked.connect (lambda: (self.records.show(), self.close()))
        self.btnViewL.clicked.connect (lambda: (self.view_logs.show(), self.close()))
        self.add.btnCancel2.clicked.connect (lambda: (self.add.close(), self.show()))
        self.restock.btnCancel3.clicked.connect (lambda: (self.restock.close(), self.show()))
        self.records.btnCancel.clicked.connect (lambda: (self.records.close(), self.show()))
        self.view_logs.btnCancel.clicked.connect (lambda: (self.view_logs.close(), self.show()))
        
class add(QtWidgets.QMainWindow,):
    def __init__(self):
        super(add, self).__init__()
        uic.loadUi('add_edit.ui', self)

    def display(self):
        if self.lbladd_edit.text() == "Add New Item":
            self.txtProID.setText(" ")
            self.clear_fields()
        elif self.lbladd_edit.text() == "Edit Item":
            pass
            
    def clear_fields(self):
        for e in self.findChildren(QtWidgets.QLineEdit):
            e.clear()
        self.txtSpecs.toPlainText() == " "

# class edit(QtWidgets.QMainWindow):
#     def __init__(self):
#         super(edit, self).__init__()
#         uic.loadUi('add_edit.ui', self)
#         self.lbladd_edit.setText('Edit Window')

#     def display(self):
#         self.show()
        
class restock(QtWidgets.QMainWindow):
    def __init__(self):
        super(restock, self).__init__()
        uic.loadUi('restock.ui', self)

    def display(self):
        self.show()

class records(QtWidgets.QMainWindow,):
    def __init__(self):
        super(records, self).__init__()
        uic.loadUi('cust_rec.ui', self)

    def display(self):
        self.show()

class view_logs(QtWidgets.QMainWindow,):
    def __init__(self):
        super(view_logs, self).__init__()
        uic.loadUi('view_logs.ui', self)

    def display(self):
        self.show()

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
    
    def checkout(self):
        pass
        


class CheckOut (QtWidgets.QMainWindow):
       def __init__(self):
        super(CheckOut, self).__init__()
        uic.loadUi('Checkout_Page.ui', self)

    
app = QtWidgets.QApplication(sys.argv)
splash = LogIn()
splash.show()
app.exec_()