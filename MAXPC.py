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

logs_table = ['action_id', 'username', 'action', 'timestamp']



class Fields():
    add_edit_fields={'txtName':1,'txtQty':1,'txtUP':1,'txtSpecs':1}
    tblInfo_Fields=['action_id','username','timestamp','action']
    current_user = ''

class Actions:
    def prompt(self, title, message, action, icon, window=''):
        msg = QMessageBox()
        msg.setIcon(icon)
        reply=msg.question(self, title, message, QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            if window == '':
                action()
            else:
                action(window)
        else:
            pass
    
    def messages(self, message_type, title, message, selection = 'Ok'): # call if only one button is needed
        dialog = eval('QMessageBox.'+message_type)(self, title, message, eval('QMessageBox.'+selection))
    
    def show_choice(self, message_type, title, message, selection1 = 'Cancel', selection2 = 'Ok'): # call if two buttons are needed
        dialog = eval('QMessageBox.'+message_type)(self, title, message, eval('QMessageBox.'+selection1+ '| QMessageBox.'+ selection2))
        return dialog

    def go_back(self, window=''):
        eval('self.'+window).close()
        self.show()

    def clear_fields(self,fields,window=''):
        if window=='':
            for name_key in fields.keys():
                eval("self."+name_key+".clear()")
        else:
            for name_key in fields.keys():
                eval("self."+window+name_key+".clear()")


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
        cursor.execute(query_string)
        records = cursor.fetchall()
        return records
    
    def exec_query (self,query_string,data_string):
        sqliteConnection = sqlite3.connect('maxpc.db')
        cursor = sqliteConnection.cursor()
        cursor.execute(query_string, data_string)
        sqliteConnection.commit()
        cursor.close()

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
            self.messages('critical', 'Database Error!', 'An error occured while creating ID!')

class Action_Logger(ID_creator, Actions, Fields):
    def log_action(self, calltype, product_name = '', restock_value = '', sold_to = '', purchase_count = '', category = ''):
        try:
            self.main = Main_Program()
            self.id = self.create_ID('Action_Logs', 'action_id')
            date = datetime.today()
            self.action_type = calltype
            self.user = self.current_user

            if self.action_type == 'add':
                self.run_query(f"INSERT INTO Action_Logs (action_id, username, action, timestamp) VALUES ('{self.id}', '{self.user}', 'Product {product_name} Added!', '{date}')")
            elif self.action_type == 'edit':
                self.run_query(f"INSERT INTO Action_Logs (action_id, username, action, timestamp) VALUES ('{self.id}', '{self.user}', '{product_name} Details Edited!', '{date}')")
            elif self.action_type == 'delete':
                self.run_query(f"INSERT INTO Action_Logs (action_id, username, action, timestamp) VALUES ('{self.id}', '{self.user}', 'Product {product_name} Deleted!', '{date}')")
            elif self.action_type == 'restock':
                self.run_query(f"INSERT INTO Action_Logs (action_id, username, action, timestamp) VALUES ('{self.id}', '{self.user}', 'Restocked {product_name} x{int(restock_value)}', '{date}')")
            elif self.action_type == 'checkout':
                self.run_query(f"INSERT INTO Action_Logs (action_id, username, action, timestamp) VALUES ('{self.id}', '{self.user}', 'Sold {product_name} x{purchase_count} to {sold_to}', '{date}')")
            elif self.action_type == 'category':
                self.run_query(f"INSERT INTO Action_Logs (action_id, username, action, timestamp) VALUES ('{self.id}', '{self.user}', 'Category {category} Added!', '{date}')")
            elif self.action_type == 'login':
                self.run_query(f"INSERT INTO Action_Logs (action_id, username, action, timestamp) VALUES ('{self.id}', '{self.user}', 'Logged In!', '{date}')")
            elif self.action_type == 'logout':
                self.run_query(f"INSERT INTO Action_Logs (action_id, username, action, timestamp) VALUES ('{self.id}', '{self.user}', 'Logged Out!', '{date}')")
            else:
                pass
        except:
            self.messages('critical', 'Database Error!', 'An error occured while logging action!')

    def date_time(self):
        self.strCurrentTime = QtCore.QTime.currentTime()
        self.prt = self.strCurrentTime.toString("hh:mm:ss")
        self.strCurrentDate = self.currentDate.toString("MM.dd")
        self.update
        self.lcdDT.display(self.strCurrentDate +" "+ self.prt)
        
class add(QtWidgets.QMainWindow, DataBase):
    def __init__(self):
        super(add, self).__init__()
        uic.loadUi('add_edit.ui', self)

    def display(self):
        if self.lbladd_edit.text() == "Add New Item":
            self.txtProID.setText(" ")
            self.clear_fields(self.add_edit_fields)
        elif self.lbladd_edit.text() == "Edit Item":
            pass
        
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
        

        
class category(QtWidgets.QMainWindow, DataBase, Actions):
    def __init__(self):
        super(category, self).__init__()
        uic.loadUi('Category_Editor.ui', self)
        

    def display(self):
        self.show()
        self.cmbState.setCurrentIndex(0)
        self.cmbCat.setCurrentIndex(0)   

class LogIn (QSplashScreen, Action_Logger, Actions, Fields):
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
            self.current_user = username
            self.main.txtCrntUsr.setText(f"Welcome, {username}")
            self.log_action('login')
        elif username == userlist[1] and password == passwords[1]:
            self.close()
            self.main.show()
            self.current_user = username
            self.main.txtCrntUsr.setText(f"Welcome, {username}")
            self.log_action('login')
        else:
            self.messages('warning', 'Error!', 'Access Denied!')

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

# class SetupTable:

#     def setup_table(self,ccount,tname,classname=''):
#         eval('self.'+classname+tname).clear()
#         eval('self.'+classname+tname).setRowCount(4) # headers # 1st row for 1st data
#         eval('self.'+classname+tname).setColumnCount(len(ccount)) # columns count

#         for cname in range(len(ccount)):
#             eval('self.'+classname+tname).setItem(0,cname,QtWidgets.QTableWidgetItem(ccount[cname]))
#         eval('self.'+classname+tname).verticalHeader().setVisible(False)
#         eval('self.'+classname+tname).horizontalHeader().setVisible(False)
#         eval('self.'+classname+tname).setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

# class SetupTable:
#     def setup_table(self, tname, cnames, classname=''):
#         eval('self.'+classname+tname).clear()
#         eval('self.'+classname+tname).setRowCount(0)
#         eval('self.'+classname+tname).setColumnCount(len(cnames))

#         for i, cname in enumerate(cnames):
#             eval('self.'+classname+tname).setHorizontalHeaderItem(i, QtWidgets.QTableWidgetItem(cname))

#         eval('self.'+classname+tname).verticalHeader().setVisible(False)
#         eval('self.'+classname+tname).horizontalHeader().setVisible(True)
#         eval('self.'+classname+tname).setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        
class Main_Program(QtWidgets.QMainWindow, Action_Logger,Actions, Fields):
    def __init__(self):
        super(Main_Program, self).__init__()
        uic.loadUi('main.ui', self)
        self.add = add()
        self.restock = restock()
        self.checkout = CheckOut()
        self.records = records()
        self.view_logs = view_logs()
        self.ctgry = category()
        self.currentDate = QDate.currentDate()
        self.timer = QTimer()
        self.timer.start(1000)
        self.timer.timeout.connect(self.date_time)
        self.btnAdd.clicked.connect (lambda: (self.add.show(), self.close(), self.add.lbladd_edit.setText('Add New Item')))
        self.btnEdit.clicked.connect (lambda: (self.add.show(), self.close(), self.add.lbladd_edit.setText('Edit Item')))
        self.btnRestock.clicked.connect (lambda: (self.restock.show(), self.close()))
        self.btnSell.clicked.connect (lambda: (self.close(), self.checkout.open_checkout()))
        self.btnCustR.clicked.connect (lambda: (self.records.show(), self.close()))
        self.btnViewL.clicked.connect (lambda: (self.show_logs(), self.close()))
        self.btnCtgry.clicked.connect (lambda: (self.ctgry.display(), self.close(), self.showList()))
        self.btnLogOut.clicked.connect (lambda: (self.close()))
        # self.add.btnProc.clicked.connect (lambda: self.prompt('Add Item', 'Are you sure you want to add item', self.add_item, QMessageBox.Information))
        self.add.btnProc.clicked.connect (lambda: self.add_item())
        self.ctgry.btnNew.clicked.connect (lambda: (self.add_category(), self.showList()))
        self.ctgry.cmbState.currentTextChanged.connect (lambda: self.btnTxt_change())
        self.add.btnCancel2.clicked.connect (lambda: self.prompt('Return', 'Are you sure you want to go back?', self.go_back, QMessageBox.Information, 'add'))
        self.restock.btnCancel3.clicked.connect (lambda: self.prompt('Return', 'Are you sure you want to go back?', self.go_back, QMessageBox.Information, 'restock'))
        self.checkout.btnCancel.clicked.connect (lambda: self.prompt('Return', 'Are you sure you want to go back?', self.go_back, QMessageBox.Information, 'checkout'))
        self.records.btnCancel.clicked.connect (lambda: self.prompt('Return', 'Are you sure you want to go back?', self.go_back, QMessageBox.Information, 'records'))
        self.view_logs.btnCancel.clicked.connect (lambda: self.prompt('Return', 'Are you sure you want to go back?', self.go_back, QMessageBox.Information, 'view_logs'))
        self.ctgry.btnCancel4.clicked.connect (lambda: self.prompt('Return', 'Are you sure you want to go back?', self.go_back, QMessageBox.Information, 'ctgry'))
        


    def date_time(self):
        self.strCurrentTime = QtCore.QTime.currentTime()
        self.prt = self.strCurrentTime.toString("hh:mm:ss")
        self.strCurrentDate = self.currentDate.toString("MM.dd")
        self.update
        self.lcdDT.display(self.strCurrentDate +" " + self.prt)
        
    def add_item(self):
        self.id = self.create_ID('Products', 'prod_id')
        prod_name = self.add.txtName.text()
        query=f"INSERT INTO Products (prod_id, prod_name, category, brand, model, qty, specs, price) VALUES ('{self.id}', '{prod_name}', '{self.add.cmbCtgry.currentText()}', '{self.add.txtBrand.text()}', '{self.add.txtModel.text()}', '{self.add.txtQty.text()}', '{self.add.txtSpecs.toPlainText()}', '{self.add.txtUP.text()}')"
        self.run_query(query)
        self.log_action('add', prod_name)
        self.messages('information', 'Success!', f'Product {prod_name} Added!')
        
    def add_category(self):
        self.cat_input, ok = QInputDialog.getText(self, "Add Category", "Enter Category Name:", QLineEdit.Normal)
        if ok:
            query = f"INSERT INTO Category (State, Category) VALUES ('{self.ctgry.cmbState.currentText()}', '{self.cat_input}')"
            self.run_query(query)
            self.messages('information', 'Success!', f'Category {self.cat_input} Added!')
            self.log_action('category', self.cat_input)
            self.showList()
        else:
            pass

    def btnTxt_change(self):
        if self.ctgry.cmbState.currentText() == "Brand New":
            self.ctgry.btnNew.setText("Add New Category (Brand New)")
            self.showList()
            self.cmb_change()
        elif self.ctgry.cmbState.currentText() == "2nd Hand":
            self.ctgry.btnNew.setText("Add New Category (2nd Hand)")
            self.showList()
            self.cmb_change()

    def cmb_change(self):
        query = f"SELECT Category FROM Category WHERE State = '{self.ctgry.cmbState.currentText()}'"
        records = self.fetcher(query)
        self.ctgry.cmbCat.clear()
        for cat in range(len(records)):
            self.ctgry.cmbCat.addItem(records[cat][0])

    def showList(self):
        self.cmb_change()
        temp_list = []
        temp_list.clear()
        query = f"SELECT Category FROM Category WHERE State = '{self.ctgry.cmbState.currentText()}'"
        records = self.fetcher(query)
        for cat in range(len(records)):
            temp_list.append(records[cat][0])

        display = '\n'.join(temp_list)
        self.ctgry.txtList.setPlainText(display)
    
    # def actionlogs(self):
    #     command = "SELECT action_id,username,timestamp,action from Action_Logs"
    #     tblInfo_Fields2=self.fetcher(command)
    #     return tblInfo_Fields2

    def setupTable(self,tables,classname,tablename):
        eval('self.'+classname+tablename).clear()
        eval('self.'+classname+tablename).setRowCount(2) # headers # 1st row for 1st data
        eval('self.'+classname+tablename).setColumnCount(len(tables)) # columns count
        for column in range(len(tables)):
            eval('self.'+classname+tablename).setItem(0,column,QtWidgets.QTableWidgetItem(tables[column]))
        eval('self.'+classname+tablename).verticalHeader().setVisible(False)
        eval('self.'+classname+tablename).horizontalHeader().setVisible(False)
        eval('self.'+classname+tablename).setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)


    def show_table(self,classname,tablename,fetch):
        query = fetch
        data = self.fetcher(query)
        for column in range(len(data)):
            currentRowCount = eval('self.'+classname+tablename).rowCount()-1
            eval('self.'+classname+tablename).insertRow(currentRowCount)
            for item in range(len(data[column])):
                eval('self.'+classname+tablename).setItem(currentRowCount, item, QtWidgets.QTableWidgetItem(str(data[column][item])))  

    def show_logs(self):
        self.view_logs.show()
        self.setupTable(logs_table,'view_logs','.tblLogs')
        self.show_table('view_logs','.tblLogs', "SELECT action_id,username,timestamp,action from Action_Logs")

app = QtWidgets.QApplication(sys.argv)
splash = LogIn()
splash.show()
app.exec_()