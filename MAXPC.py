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

# action_type = {'add_item': 3, 'record_customer': 2, 'edit': 1, 'delete': 1, 'restock': 1, 'checkout': 4, 'login': 5, 'logout': 5}
# action = ['add_item', 'record_customer', 'edit', 'delete', 'restock', 'checkout', 'login', 'logout']
# ids = ['username', 'action_id', 'customer_id', 'prod_id', 'trans_id']

class DataBase:
    def run_query(self, query_string):
        sqliteConnection = sqlite3.connect('maxpc.db')
        cursor = sqliteConnection.cursor()
        perform = cursor.execute(query_string)
        sqliteConnection.commit()
        cursor.close()
    
    def fetcher(self, query_string):
        sqliteConnection = sqlite3.connect('maxpc.db')
        cursor = sqliteConnection.cursor()
        print("Database Connected!")
        command = query_string
        cursor.execute(command)
        records = cursor.fetchall()
        return records

class Dialog(DataBase):
    def show_dialog(self, message_type, title, message, selection = 'Ok'): # call if only one button is needed
        dialog = eval('QMessageBox.'+message_type)(self, title, message, eval('QMessageBox.'+selection))
    
    def show_choice(self, message_type, title, message, selection1 = 'Cancel', selection2 = 'Ok'): # call if two buttons are needed
        dialog = eval('QMessageBox.'+message_type)(self, title, message, eval('QMessageBox.'+selection1+ '| QMessageBox.'+ selection2))
        return dialog

class ID_creator(DataBase):
    def create_ID(self, table, col):
        try:
            current_ID = ''
            change_to = ''
            if table == 'Action_Logs':
                current_ID = 'ACT01'
                change_to = 'ACT0'
            elif table == 'Products':
                current_ID = 'PRD01'
                change_to = 'PRD0'
            elif table == 'Customer_Info':
                current_ID = 'CST01'
                change_to = 'CST0'
            elif table == 'Output_Logs':
                current_ID = 'OUT01'
                change_to = 'OUT0'
            else:
                pass

            query = f"SELECT {col} FROM {table}"
            records = self.fetcher(query)
            count=1
            setID = current_ID
            if records==[]:
                setID = current_ID
            else:
                for i in range(len(records)):
                    while setID == records[i][0]:
                        count = int(setID.replace(change_to,''))
                        count += 1
                        setID = change_to+str(count)
            return setID
        except:
            self.show_dialog('critical', 'Database Error!', 'An error occured while creating ID!')

class Action_Logger(ID_creator, Dialog):
    def log_action(self, calltype, username, product_name = '', restock_value = '', sold_to = '', purchase_count = ''):
        try:
            self.main = Main_Program()
            self.id = self.create_ID('Action_Logs', 'action_id')
            date = datetime.today()
            self.action_type = self.main.txtCrntUsr.replace('Welcome, ', '')
            self.user = username

            if self.action_type == 'add':
                self.run_query(f"INSERT INTO Action_Logs (action_id, username, timestamp, action) VALUES ('{self.id}', '{self.user}', 'Product {product_name} Added!', '{date}')")
            elif self.action_type == 'edit':
                self.run_query(f"INSERT INTO Action_Logs (action_id, username, timestamp, action) VALUES ('{self.id}', '{self.user}', 'Details Edited!', '{date}')")
            elif self.action_type == 'delete':
                self.run_query(f"INSERT INTO Action_Logs (action_id, username, timestamp, action) VALUES ('{self.id}', '{self.user}', 'Product Deleted!', '{date}')")
            elif self.action_type == 'restock':
                self.run_query(f"INSERT INTO Action_Logs (action_id, username, timestamp, action) VALUES ('{self.id}', '{self.user}', 'Restocked {product_name} x{int(restock_value)}', '{date}')")
            elif self.action_type == 'checkout':
                self.run_query(f"INSERT INTO Action_Logs (action_id, username, timestamp, action) VALUES ('{self.id}', '{self.user}', 'Sold {product_name} x{purchase_count} to {sold_to}', '{date}')")
            elif self.action_type == 'login':
                self.run_query(f"INSERT INTO Action_Logs (action_id, username, timestamp, action) VALUES ('{self.id}', '{self.user}', 'Logged In!', '{date}')")
            elif self.action_type == 'logout':
                self.run_query(f"INSERT INTO Action_Logs (action_id, username, timestamp, action) VALUES ('{self.id}', '{self.user}', 'Logged Out!', '{date}')")
            else:
                pass
        except:
            self.show_dialog('critical', 'Database Error!', 'An error occured while logging action!')
        

class Main_Program(QtWidgets.QMainWindow, Action_Logger):
    def __init__(self):
        super(Main_Program, self).__init__()
        uic.loadUi('main.ui', self)
        self.add = add()
        self.restock = restock()
        self.checkout = CheckOut()
        self.records = records()
        self.view_logs = view_logs()
        self.currentDate = QDate.currentDate()
        self.timer = QTimer()
        self.timer.start(1000)
        self.timer.timeout.connect(self.date_time)
        self.btnAdd.clicked.connect (lambda: (self.add.show(), self.close(), self.add.lbladd_edit.setText('Add New Item'), self.add.display()))
        self.btnEdit.clicked.connect (lambda: (self.add.show(), self.close(), self.add.lbladd_edit.setText('Edit Item'), self.add.display()))
        self.btnRestock.clicked.connect (lambda: (self.restock.show(), self.close()))
        self.btnCustR.clicked.connect (lambda: (self.records.show(), self.close()))
        self.btnViewL.clicked.connect (lambda: (self.view_logs.show(), self.close()))
        self.btnLogOut.clicked.connect (lambda: (self.close()))
        self.add.btnCancel2.clicked.connect (lambda: (self.add.close(), self.show()))
        self.restock.btnCancel3.clicked.connect (lambda: (self.restock.close(), self.show()))
        self.btnSell.clicked.connect (lambda: (self.close(), self.checkout.open_checkout()))
        self.checkout.btnCancel.clicked.connect (lambda: (self.checkout.close(), self.show()))
        self.records.btnCancel.clicked.connect (lambda: (self.records.close(), self.show()))
        self.view_logs.btnCancel.clicked.connect (lambda: (self.view_logs.close(), self.show()))

    def date_time(self):
        self.strCurrentTime = QtCore.QTime.currentTime()
        self.prt = self.strCurrentTime.toString("hh:mm:ss")
        self.strCurrentDate = self.currentDate.toString("MM.dd")
        self.update
        self.lcdDT.display(self.strCurrentDate +" " + self.prt)
        
class add(QtWidgets.QMainWindow, DataBase):
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

        
class restock(QtWidgets.QMainWindow, DataBase):
    def __init__(self):
        super(restock, self).__init__()
        uic.loadUi('restock.ui', self)

    def display(self):
        self.show()

class records(QtWidgets.QMainWindow, DataBase):
    def __init__(self):
        super(records, self).__init__()
        uic.loadUi('cust_rec.ui', self)

    def display(self):
        self.show()

class view_logs(QtWidgets.QMainWindow, DataBase):
    def __init__(self):
        super(view_logs, self).__init__()
        uic.loadUi('view_logs.ui', self)

    def display(self):
        self.show()

class LogIn (QSplashScreen, Action_Logger, Dialog):
    def __init__(self):
        super(LogIn, self).__init__()
        uic.loadUi('login.ui', self)
        self.closeSplash()
        self.main = Main_Program()
        self.fetcher = DataBase().fetcher
        self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)
        pixmap = QPixmap("SplashBG.png")
        pixmap = pixmap.scaled(850, 850, Qt.KeepAspectRatio)
        self.setPixmap(pixmap)
        self.btnLogIn.clicked.connect(lambda: self.check_login())
        self.btnCancel.clicked.connect(lambda: self.closeSplash())

    def check_login(self):
        username = self.txtUsername.text()
        password = self.txtPassword.text()
        data = self.fetcher("SELECT * FROM Accounts")
        userlist = []
        passwords = []
        for da in range(len(data)):
            usr = data[da][0]
            userlist.append(usr)
            pwd = data[da][1]
            passwords.append(pwd)
        if username == userlist[0] and password == passwords[0]:
            self.close()
            self.main.show()
            self.main.txtCrntUsr.setText(f"Welcome, {username}")
            self.log_action('login', username)
        elif username == userlist[1] and password == passwords[1]:
            self.close()
            self.main.show()
            self.main.txtCrntUsr.setText(f"Welcome, {username}")
            self.log_action('login', username)
        else:
            self.show_choice('warning', 'Error!', 'Access Denied!')   

    def closeSplash(self):
        self.close()

    def mousePressEvent(self, event): 
        pass # disable default "click-to-dismiss" behaviour
        


class CheckOut (QtWidgets.QMainWindow, DataBase):
    def __init__(self):
        super(CheckOut, self).__init__()
        uic.loadUi('Checkout_Page.ui', self)
        
    def open_checkout(self):
        self.show()
        
    
app = QtWidgets.QApplication(sys.argv)
splash = LogIn()
splash.show()
app.exec_()