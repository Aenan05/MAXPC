from types import NoneType
import typing
from PyQt5 import QtCore, QtWidgets, QtPrintSupport, uic
import sys
import sqlite3
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWidgets import QWidget
from PyQt5.uic import loadUi
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPixmap
from datetime import datetime, date as current, timedelta
from PyQt5.QtCore import QDate
from PyQt5.QtGui import QColor
import random
import re
import time
from PyQt5.QtGui import QPainter, QPdfWriter
from PyQt5.QtCore import Qt, QMarginsF
from pathlib import Path, PurePath
import shutil
# import pandas as pd
# import easygui as eg
# from openpyxl import Workbook
import os

# action_type = {'add_item': 3, 'record_customer': 2, 'edit': 1, 'delete': 1, 'restock': 1, 'checkout': 4, 'login': 5, 'logout': 5}
# action = ['add_item', 'record_customer', 'edit', 'delete', 'restock', 'checkout', 'login', 'logout']
# ids = ['username', 'action_id', 'customer_id', 'prod_id', 'trans_id']

sales_table = ['Transaction ID', 'Date', 'Username', 'Product ID', 'Product Name', 'Customer ID', 'Customer Name', 'Quantity', 'Total Price']
logs_table = ['Action ID', 'Username', 'Timestamp', 'Action']
cust_table= ['Customer ID', 'Customer Name', 'Customer Address','Phone Number']
current_user = {'username': ''}
tblInfo_Fields_main = ['ID','State', 'Category', 'Name','Quantity','Unit Price']
display_fields = ['txtID', 'txtState', 'txtCat', 'txtName', 'txtBrand', 'txtModel', 'txtQty', 'txtUP']
edit_fields = ['txtProID', 'txtName', 'txtBrand', 'txtModel', 'txtQty', 'txtUP']
selected_items = []
selected_items_name = []
selected_items_quantity = []
selected_items_total_per_item = []

class Fields():
    add_edit_fields={'txtName':3,'txtQty':1,'txtUP':1,'txtSpecs':3,'txtBrand':3,'txtModel':3}
    display_fields2 = {'txtID':3, 'txtState':3, 'txtCat':3, 'txtName':3, 'txtBrand':3, 'txtModel':3, 'txtQty':1, 'txtUP':1}
    sell_fields = {'txtCustName':3, 'txtCustAdd':3, 'txtCustContact':3}
    tblInfo_Fields=['ID','Username','Timestamp','Action']
    
class Actions(Fields):
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

    def logout(self):
        self.login=LogIn()
        self.close()
        self.login.show()
    
    def messages(self, message_type, title, message, selection = 'Ok'): # call if only one button is needed
        dialog = eval('QMessageBox.'+message_type)(self, title, message, eval('QMessageBox.'+selection))
    
    def show_choice(self, message_type, title, message, selection1 = 'Cancel', selection2 = 'Ok'): # call if two buttons are needed
        dialog = eval('QMessageBox.'+message_type)(self, title, message, eval('QMessageBox.'+selection1+ '| QMessageBox.'+ selection2))
        return dialog

    def go_back(self, window=''):
        self.clear_fields(self.add_edit_fields, 'add.')
        eval('self.'+window).close()
        self.show()

    def clear_fields(self,fields,window=''):
        if window=='':
            for name_key in fields.keys():
                eval("self."+name_key+".clear()")
        else:
            for name_key in fields.keys():
                eval("self."+window+name_key+".clear()")

class Validator:
    num_reg_ex = QRegExp("^[0-9]{0,9}$")
    def check (self, fields,window=''):
        if window == '':
            for name_key,checker in fields.items():
                if checker == 1:
                    eval("self."+name_key).setValidator(QRegExpValidator(self.num_reg_ex))
        else:
            for name_key,checker in fields.items():
                if checker == 1:
                    eval("self."+window+name_key).setValidator(QRegExpValidator(self.num_reg_ex))   

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

class ID_creator(DataBase):
    def create_ID(self, table, col):
        try:
            current_ID = ''
            change_to = ''
            if table == 'Action_Logs':
                current_ID = 'ACT01'
                change_to = 'ACT0'
            elif table == 'Used_ID':
                current_ID = 'PRD01'
                change_to = 'PRD0'
            elif table == 'Customer_Info':
                current_ID = 'CST01'
                change_to = 'CST0'
            elif table == 'Output_Logs':
                current_ID = 'MAX01'
                change_to = 'MAX0'
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
    def log_action(self, calltype, product_name = '', restock_value = '', sold_to = '', purchase_count = '', category = '', State = '', quantity = '', forclean = '', category_turninto=''):
        try:
            self.main = Main_Program()
            self.id = self.create_ID('Action_Logs', 'action_id')
            date = datetime.today()
            self.action_type = calltype
            self.user = current_user['username']

            if self.action_type == 'add':
                self.run_query(f"INSERT INTO Action_Logs (action_id, username, action, timestamp) VALUES ('{self.id}', '{self.user}', 'Product {product_name} x{quantity} Added!', '{date}')")
            elif self.action_type == 'edit':
                self.run_query(f"INSERT INTO Action_Logs (action_id, username, action, timestamp) VALUES ('{self.id}', '{self.user}', '{product_name} Details Edited!', '{date}')")
            elif self.action_type == 'delete':
                self.run_query(f"INSERT INTO Action_Logs (action_id, username, action, timestamp) VALUES ('{self.id}', '{self.user}', 'Product {product_name} Deleted!', '{date}')")
            elif self.action_type == 'restock':
                self.run_query(f"INSERT INTO Action_Logs (action_id, username, action, timestamp) VALUES ('{self.id}', '{self.user}', 'Restocked {product_name} x{int(restock_value)}', '{date}')")
            elif self.action_type == 'checkout':
                self.run_query(f"INSERT INTO Action_Logs (action_id, username, action, timestamp) VALUES ('{self.id}', '{self.user}', 'Sold {product_name} x{int(purchase_count)} to {sold_to}', '{date}')")
            elif self.action_type == 'category':
                self.run_query(f"INSERT INTO Action_Logs (action_id, username, action, timestamp) VALUES ('{self.id}', '{self.user}', 'Category {category} added in {State}!', '{date}')")
            elif self.action_type == 'category edit':
                self.run_query(f"INSERT INTO Action_Logs (action_id, username, action, timestamp) VALUES ('{self.id}', '{self.user}', 'Category {category} rename to {category_turninto}!', '{date}')")
            elif self.action_type == 'category delete':
                self.run_query(f"INSERT INTO Action_Logs (action_id, username, action, timestamp) VALUES ('{self.id}', '{self.user}', 'Category {category} Removed!', '{date}')")
            elif self.action_type == 'category remove product':
                self.run_query(f"INSERT INTO Action_Logs (action_id, username, action, timestamp) VALUES ('{self.id}', '{self.user}', 'Product {product_name} deleted due to category deletion!', '{date}')")
            elif self.action_type == 'login':
                self.run_query(f"INSERT INTO Action_Logs (action_id, username, action, timestamp) VALUES ('{self.id}', '{self.user}', 'Logged In!', '{date}')")
            elif self.action_type == 'logout':
                self.run_query(f"INSERT INTO Action_Logs (action_id, username, action, timestamp) VALUES ('{self.id}', '{self.user}', 'Logged Out!', '{date}')")
            elif self.action_type == 'backup':
                self.run_query(f"INSERT INTO Action_Logs (action_id, username, action, timestamp) VALUES ('{self.id}', '{self.user}', 'Backup Created!', '{date}')")
            elif self.action_type == 'cleanup':
                self.run_query(f"INSERT INTO Action_Logs (action_id, username, action, timestamp) VALUES ('{self.id}', '{self.user}', 'Data in {forclean} has been cleaned!', '{date}')")
            elif self.action_type == 'restore':
                self.run_query(f"INSERT INTO Action_Logs (action_id, username, action, timestamp) VALUES ('{self.id}', '{self.user}', 'Data Restored!', '{date}')")
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

class BaseWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(BaseWindow, self).__init__()
        self.main_program = Main_Program
        
    def display(self):
        self.show()
        self.update_theme()  # Update the theme when the window is displayed

    def update_theme(self):
        query = "SELECT Value FROM Settings WHERE Setting = 'theme'"
        view = self.fetcher(query)

        if view[0][0] == 'Dark':
            self.main_program.dark_theme_text(self)
            self.main_program.dark_theme_label(self)
        elif view[0][0] == 'Light':
            self.main_program.light_theme_text(self)

class ThemeWindow(BaseWindow):
    def __init__(self):
        super(ThemeWindow, self).__init__()

    def display(self):
        super().display()

    def theme_checkbox_changed(self, state):
        if state == QtCore.Qt.Checked:
            self.update_theme()  # Update the theme when the checkbox is checked
        else:
            # Handle theme reset or other actions when the checkbox is unchecked
            pass

       

class add(ThemeWindow,QtWidgets.QMainWindow, ID_creator, DataBase, Actions, Fields):
    def __init__(self):
        super(add, self).__init__()
        uic.loadUi('add_edit.ui', self)
        
              
class restock(ThemeWindow, QtWidgets.QMainWindow, DataBase):
    def __init__(self):
        super(restock, self).__init__()
        uic.loadUi('restock.ui', self)
       

class records(ThemeWindow, QtWidgets.QMainWindow, DataBase):
    def __init__(self):
        super(records, self).__init__()
        uic.loadUi('cust_rec.ui', self)

class view_logs(ThemeWindow, QtWidgets.QMainWindow, DataBase):
    def __init__(self):
        super(view_logs, self).__init__()
        uic.loadUi('view_logs.ui', self)
        self.main_program = Main_Program


class sales_records(ThemeWindow, QtWidgets.QMainWindow, DataBase):
    def __init__(self):
        super(sales_records, self).__init__()
        uic.loadUi('sales_records.ui', self)
           
class category(ThemeWindow,QtWidgets.QMainWindow, DataBase, Actions):
    def __init__(self):
        super(category, self).__init__()
        uic.loadUi('Category_Editor.ui', self)

class Receipt(QtWidgets.QMainWindow):
    def __init__(self):
        super(Receipt, self).__init__()
        uic.loadUi('Receipt.ui', self)

class Admin_Panel(ThemeWindow, QtWidgets.QMainWindow, DataBase, Actions):
    def __init__(self):
        super(Admin_Panel, self).__init__()
        uic.loadUi('admin_panel.ui', self)
        
   
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
        self.btnCancel.clicked.connect(lambda: (self.closeSplash()))

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
            self.messages('information', 'Please Wait', 'Loading Inventory...')
            if QMessageBox.Ok:
                current_user['username'] = username
                self.close()
                self.main.show()
                self.main.txtCrntUsr.setText(f"Welcome, {username}")
                self.main.check_auth(current_user['username'])
                self.log_action('login')
        elif username == userlist[1] and password == passwords[1]:
            self.messages('information', 'Please Wait', 'Loading Inventory...')
            if QMessageBox.Ok:
                current_user['username'] = username
                self.close()
                self.main.show()
                self.main.txtCrntUsr.setText(f"Welcome, {username}")
                self.main.check_auth(current_user['username'])
                self.log_action('login')
        else:
            self.messages('warning', 'Error!', 'Access Denied!')

    def closeSplash(self):
        self.close()

    def mousePressEvent(self, event): 
        pass # disable default "click-to-dismiss" behaviour

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Return:
            self.check_login()

class CheckOut (QtWidgets.QMainWindow, DataBase):
    def __init__(self):
        super(CheckOut, self).__init__()
        uic.loadUi('Checkout_Page.ui', self)
        self.main_program = Main_Program
        
    def open_checkout(self):
    
        query = "SELECT Value FROM Settings WHERE Setting = 'theme'"
        admin_view = self.fetcher(query)

        if admin_view[0][0] == 'Dark':
            self.main_program.dark_theme_text(self) 
            self.main_program.dark_theme_label(self)
           
        elif admin_view[0][0] == 'Light':
            self.main_program.light_theme_text(self) 

class Receipt (QtWidgets.QMainWindow, DataBase):
    def __init__(self):
        super(Receipt, self).__init__()
        uic.loadUi('Receipt.ui', self)

    def open_receipt(self):
        self.show()

class SetupTable:
    def setupTable(self,tables,classname='',tablename=''):
        eval('self.'+classname+tablename).clear()
        eval('self.'+classname+tablename).setRowCount(2) # headers # 1st row for 1st data
        eval('self.'+classname+tablename).setColumnCount(len(tables)) # columns count
        for column in range(len(tables)):
            eval('self.'+classname+tablename).setItem(0,column,QtWidgets.QTableWidgetItem(tables[column]))
        eval('self.'+classname+tablename).verticalHeader().setVisible(False)
        eval('self.'+classname+tablename).horizontalHeader().setVisible(False)
        eval('self.'+classname+tablename).horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        eval('self.'+classname+tablename).setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        eval('self.'+classname+tablename).verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

    def show_table(self,classname,tablename,fetch):
        query = fetch
        data = self.fetcher(query)
        for column in range(len(data)):
            currentRowCount = eval('self.'+classname+tablename).rowCount()-1
            eval('self.'+classname+tablename).insertRow(currentRowCount)
            for item in range(len(data[column])):
                eval('self.'+classname+tablename).setItem(currentRowCount, item, QtWidgets.QTableWidgetItem(str(data[column][item])))


class Main_Program(QtWidgets.QMainWindow, Action_Logger, ID_creator, Actions, Fields, SetupTable, Validator):
    def __init__(self):
        super(Main_Program, self).__init__()
        uic.loadUi('main.ui', self)
        self.add = add()
        self.restock = restock()
        self.checkout = CheckOut()
        self.records = records()
        self.sales_records= sales_records()
        self.view_logs = view_logs()
        self.ctgry = category()
        self.receipt = Receipt()
        self.settings = Admin_Panel()
        self.currentDate = QDate.currentDate()
        self.timer = QTimer()
        self.timer.start(1000)
        self.check(self.add_edit_fields,'add.')
        self.check_auth(current_user['username'])
        self.current_item = ''
        self.current_item_name = ''
        self.current_qty = ''
        self.current_price = ''
        self.current_theme = ''
        self.local_backup_state = ''
        self.local_backup_directory = ''
        self.backup_days = ''
        self.online_backup_state = ''
        self.online_backup_email = ''
        self.setupTable(tblInfo_Fields_main, '', 'tblData')
        self.show_table('','tblData', "SELECT prod_id, state, category, prod_name, qty, price FROM Products WHERE state = 'Brand New'")
        self.timer.timeout.connect(self.date_time)
        self.btnAdd.clicked.connect (lambda: (self.clear_fields(self.add_edit_fields, 'add.'), self.add.display(), self.close(), self.add_category_setter(), self.add.lbladd_edit.setText('Add New Item'), self.add.txtProID.setText(self.create_ID('Used_ID', 'prod_id'))))
        self.btnEdit.clicked.connect (lambda: (self.add.display(), self.close(), self.add_category_setter(), self.add.lbladd_edit.setText('Edit Item'), self.edit_item()))
        self.btnRestock.clicked.connect (lambda: (self.restock_item(),self.close(),self.restock.display()))
        self.btnSell.clicked.connect (lambda: (self.display_checkout(),self.checkout.open_checkout()))
        self.btnCustR.clicked.connect (lambda: (self.show_customer_records(), self.close(), self.records.display()))
        self.btnSalesRec.clicked.connect (lambda: (self.show_sales_records(), self.close(),self.sales_records.display()))
        self.btnViewL.clicked.connect (lambda: (self.show_logs(), self.close(),self.view_logs.display()))
        self.btnCtgry.clicked.connect (lambda: (self.ctgry.display(), self.close(), self.showList(),self.ctgry.display()))
        self.btnSettings.clicked.connect(lambda: (self.show_settings()))
        self.btnStatus.clicked.connect(lambda: self.inv_checker())
        self.btnLogOut.clicked.connect (lambda: (self.prompt('Logout', 'Are you sure you want to logout?', self.logout, QMessageBox.Critical)))
        self.btnRemove.clicked.connect (lambda: self.prompt('Delete item', 'Are you sure you want to delete this item?', self.remove_item, QMessageBox.Critical))
        self.add.btnProc.clicked.connect (lambda: self.add_edit_item_prompt())
        self.add.cmbState.currentTextChanged.connect (lambda: self.add_category_setter())
        self.restock.btnProc2.clicked.connect (lambda: (self.prompt('Restock Item', 'Are you sure you want to restock the item?', self.restock_qty, QMessageBox.Information)))
        self.view_logs.btnSearch.clicked.connect (lambda: (self.search_table()))
        self.view_logs.btnDate.clicked.connect (lambda: (self.date_table()))
        self.view_logs.btnUndo.clicked.connect (lambda: (self.view_logs.txtSearch.clear(), self.show_logs()))
        self.ctgry.btnNew.clicked.connect (lambda: (self.add_category(), self.showList()))
        self.ctgry.cmbState.currentTextChanged.connect (lambda: self.btnTxt_change())
        self.ctgry.btnEdit.clicked.connect (lambda: (self.edit_category()))
        self.ctgry.btnRemove.clicked.connect (lambda: (self.prompt('Delete Category', 'Are you sure you want to delete this category?', self.remove_category, QMessageBox.Critical)))
        self.add.btnCancel2.clicked.connect (lambda: (self.prompt('Return', 'Are you sure you want to go back?', self.go_back, QMessageBox.Information, 'add')))
        self.restock.btnCancel3.clicked.connect (lambda: self.prompt('Return', 'Are you sure you want to go back?', self.go_back, QMessageBox.Information, 'restock'))
        self.checkout.btnCancel.clicked.connect (lambda: self.prompt('Return', 'Are you sure you want to go back?', self.go_back, QMessageBox.Information, 'checkout'))
        self.ctgry.btnCancel.clicked.connect (lambda: self.prompt('Return', 'Are you sure you want to go back?', self.go_back, QMessageBox.Information, 'ctgry'))
        self.view_logs.btnCancel4.clicked.connect (lambda: self.go_back('view_logs'))
        self.records.btnCancel2.clicked.connect (lambda: self.go_back('records'))
        self.sales_records.btnCancel.clicked.connect (lambda: self.go_back('sales_records'))
        self.sales_records.btnExcel.clicked.connect (lambda: self.excel_file())
        self.sales_records.btnWeekly.clicked.connect (lambda: self.weekly())
        self.sales_records.btnMonthly.clicked.connect (lambda: self.monthly())
        self.sales_records.txtSearch.textChanged.connect(lambda: self.search_sales_records())
        self.records.txtSearch.textChanged.connect(lambda: self.search_records())
        self.btnBrNew.setChecked(True)
        self.btnSeeAll.setChecked(True)
        self.spinQ.setEnabled(False)
        self.CatSelect.idToggled.connect(lambda: self.change_state())
        self.SortSelector.idToggled.connect(lambda: self.toggle_view())
        self.cmbCat.currentTextChanged.connect(lambda: self.sort_table_by_category())
        self.tblData.cellClicked.connect(lambda: self.show_details())
        self.btnAddSel.clicked.connect(lambda: self.add_to_selection())
        self.spinQ.valueChanged.connect(lambda: self.compute_total_per_product())
        self.btnClrSel.clicked.connect(lambda: self.remove_selections_prompt())
        self.txtSearch.textChanged.connect(lambda: self.search_inventory())
        self.checkout.grpSoldTo.idToggled.connect(lambda: self.set_customers())
        self.checkout.cmbExisting.currentTextChanged.connect(lambda: self.cmbExisting_changeIndex())
        self.checkout.btnExisting.setChecked(True)
        self.checkout.btnChckOut.clicked.connect(lambda: self.prompt("Checkout", "Are you sure you want to checkout?", self.check_details_checkout, QMessageBox.Information))
        self.receipt.btnBack.clicked.connect(lambda: (self.receipt.close(), self.checkout.show()))
        self.receipt.btnPrint.clicked.connect(lambda: self.print_file())
        self.receipt.btnDontPrint.clicked.connect(lambda: self.continue_without_receipt())
        self.settings.adminSP.clicked.connect(lambda: self.password_toggle('txtAdminP',self.settings.adminSP))
        self.settings.userSP.clicked.connect(lambda: self.password_toggle('txtUserP',self.settings.userSP))
        self.settings.btnBrowse.clicked.connect(lambda: self.path_selector())
        self.settings.LBToggle.idToggled.connect(lambda: self.LBToggle_onToggle())
        self.settings.btnApplySettings.clicked.connect(lambda: self.apply_settings())
        self.settings.cmbDays.currentTextChanged.connect(lambda: self.days_select())
        self.settings.btnCancel.clicked.connect(lambda: (self.settings.close(), self.show(), self.remove_selections_cleanup()))
        self.settings.btnExport.clicked.connect(lambda: self.manual_backup())
        self.settings.btnImport.clicked.connect(lambda: self.restore_data())
        self.settings.chkDark.toggled.connect(self.dark_theme)
        self.settings.chkLight.toggled.connect(self.light_theme)
        self.settings.themeSel.idToggled.connect(self.theme_toggle)
        self.auto_backup()
        self.auto_theme()
        self.txtSearch.setFocus()
        self.settings.grpClean.idToggled.connect(lambda: self.data_cleanup_select())
        self.settings.btnClean.clicked.connect(lambda: self.proceed_cleanup())

    def auto_theme(self):
        query = "SELECT Value FROM Settings WHERE Setting = 'theme'"
        thm = self.fetcher(query)

        if thm[0][0] == 'Dark':
            self.dark_theme(self.settings.chkDark.setChecked(True))
            
        elif thm[0][0] == 'Light':
            self.light_theme( self.settings.chkLight.setChecked(True))

    def dark_theme(self, checked):
        if checked:
            # Apply dark theme
            self.set_button_style_dark([self.btnAdd, self.btnEdit, self.btnRestock, self.btnRemove, self.settings.adminSP, self.settings.userSP])
            self.set_table_dark([self.checkout.txtCustContact,self.checkout.txtCustName,self.checkout.txtCustAdd,self.sales_records.txtSearch,self.tblData, self.txtSelect, self.txtSearch,self.add.txtSpecs,self.records.tblCust,self.view_logs.tblLogs,self.sales_records.tblSales,self.ctgry.txtList,self.checkout.txtItems])
            self.set_button_style_dark2(
                
                                        button_limegreen=[self.btnSell, self.checkout.btnChckOut, self.ctgry.btnNew, self.view_logs.btnSearch, self.add.btnProc, self.settings.btnApplySettings, self.restock.btnProc2], 

                                        button_firebrick=[self.records.btnCancel2,self.view_logs.btnCancel4,self.restock.btnCancel3,self.btnClrSel, self.view_logs.btnUndo, self.settings.btnClean, self.sales_records.btnCancel, self.checkout.btnCancel, self.ctgry.btnCancel, self.ctgry.btnRemove, self.settings.btnCancel], 

                                        button_darkkhaki=[self.ctgry.btnEdit,self.sales_records.btnMonthly,self.sales_records.btnWeekly,self.sales_records.btnExcel,self.view_logs.btnDate,self.settings.btnClean,self.settings.btnImport,self.settings.btnExport,self.add.btnCancel2, self.btnSalesRec,self.btnCtgry,self.btnSettings,self.btnStatus,self.btnCustR,self.btnViewL,self.btnAddSel])
            self.set_background_dark([self.checkout.CheckWidget,self.ctgry.CatWidget,self.settings.AdminWidget,self.centralwidget,self.add.AddWidget,self.restock.RestockWidget,self.records.CustRecWidgets,self.view_logs.ViewLogsWidget, self.sales_records.SalesWidget])
            self.dark_theme_text()
            self.dark_theme_label()
        else:
            pass
    def set_background_dark(self, bg):
        for background in bg:
            background.setStyleSheet('''
                QWidget {
                    background-color: rgb(58, 58, 58);
                }
                
            ''')
    
    def set_button_style_dark(self, buttons):
        for button in buttons:
            button.setStyleSheet('''
                QPushButton {
                    background-color: transparent;
                    color:  rgb(158, 158, 158);
                    border: 2px solid rgb(58, 58, 58);
                    border-radius: 15px;
                    padding: 5px;
                    font: 87 10pt "Arial Black";
                   
                }
                QPushButton:hover {
                    background-color: rgb(98, 98, 98);
                    color: white;
                }
            ''')
       
        
    def set_button_style_dark2(self, button_limegreen = [], button_firebrick = [], button_darkkhaki = []):
        base_style = '''
        QPushButton {
            background-color: transparent;
            color: rgb(158, 158, 158);
            border: 2px solid rgb(58, 58, 58);
            border-radius: 12px;
            padding: 3px;
            font: 87 10pt "Arial Black";
            border: 1px solid gray;
        }

        QPushButton:hover {
            color: white;
        }
    '''
        if button_limegreen == []:
            pass
        else:
            for button in button_limegreen:
                button.setStyleSheet(base_style + '''
                    QPushButton:hover {
                        background-color: limegreen;
                    }
                ''')
        if button_firebrick == []:
            pass
        else:
            for button in button_firebrick:
                button.setStyleSheet(base_style + '''
                    QPushButton:hover {
                        background-color: firebrick;
                    }
                ''')
        if button_darkkhaki == []:
            pass
        else:
            for button in button_darkkhaki:
                button.setStyleSheet(base_style + '''
                    QPushButton:hover {
                        background-color: darkkhaki;
                    }
                ''')
                 
    def set_table_dark(self, tables):
        for table in tables:
            table.setStyleSheet('''
                QTableWidget {
                    color: white;
                    border: 2px solid black;
                    gridline-color: gray;
                }
            
                QPlainTextEdit{
                    background-color: gray;
                    color: white;
                    border: 1px solid black;
                }
                QLineEdit {
                    background-color: rgb(90, 90, 90);
                    color: white;
                    border: 2px solid rgb(58, 58, 58);
                    border-radius: 10px;
                    padding: 5px;
                }
               
            ''')

    def set_background_dark(self, bg):
        for background in bg:
            background.setStyleSheet('''
                QWidget {
                    background-color: rgb(58, 58, 58);
                }
            ''')
           
    
    def light_theme(self, checked):
        if checked:
            print("Light theme selected")
            # Apply light theme
            self.set_button_style_light([self.btnSettings,self.btnStatus,self.btnAdd, self.btnEdit, self.btnRestock, self.btnRemove, self.add.btnCancel2, self.add.btnProc])
            self.set_button_style_light2(
                                        button_limegreen=[self.btnSell, self.checkout.btnChckOut, self.ctgry.btnNew, self.view_logs.btnSearch, self.add.btnProc, self.settings.btnApplySettings, self.restock.btnProc2], 

                                        button_firebrick=[self.view_logs.btnCancel4,self.restock.btnCancel3,self.btnClrSel, self.view_logs.btnUndo, self.settings.btnClean, self.sales_records.btnCancel, self.checkout.btnCancel, self.ctgry.btnCancel, self.ctgry.btnRemove, self.settings.btnCancel], 

                                        button_darkkhaki=[self.records.btnCancel2,self.ctgry.btnEdit,self.sales_records.btnMonthly,self.sales_records.btnWeekly,self.sales_records.btnExcel,self.view_logs.btnDate,self.settings.btnClean,self.settings.btnImport,self.settings.btnExport,self.add.btnCancel2, self.btnSalesRec,self.btnCtgry,self.btnSettings,self.btnStatus,self.btnCustR,self.btnViewL,self.btnAddSel])
            
            self.set_PlainText_light([self.checkout.txtCustContact,self.checkout.txtCustName,self.checkout.txtCustAdd,self.sales_records.txtSearch,self.txtSpecs,self.tblData, self.txtSelect, self.txtSearch,self.add.txtSpecs,self.records.txtSearch,self.view_logs.tblLogs,self.sales_records.tblSales,self.ctgry.txtList,self.checkout.txtItems])

            self.set_background_light([self.checkout.CheckWidget,self.ctgry.CatWidget,self.settings.AdminWidget,self.centralwidget,self.add.AddWidget,self.restock.RestockWidget,self.records.CustRecWidgets,self.view_logs.ViewLogsWidget, self.sales_records.SalesWidget])
            self.light_theme_text()
        else: 
            print("Checkbox is light")
            
    
    def set_background_light(self, bg):
        for background in bg:
            background.setStyleSheet('''
                QWidget {
                    background-color: white;
                    color: black;
                }
                
            ''')

    def set_button_style_light(self, buttons):
        for button in buttons:
            button.setStyleSheet('''
                QPushButton {
                    background-color:transparent;
                    color: black;
                   
                    border-radius: 15px;
                    padding: 5px;
                    font: 12pt "Impact";
                }
                QPushButton:hover {
                    background-color: rgb(98, 98, 98);
                    color: white;
                }
            ''')

    def set_button_style_light2(self, button_limegreen = [], button_firebrick = [], button_darkkhaki = []):
        base_style = '''
        QPushButton {
            background-color: transparent;
            color: black;
            border: 2px solid rgb(58, 58, 58);
            border-radius: 12px;
            padding: 3px;
            font: 87 10pt "Arial Black";
            border: 1px solid gray;
        }

        QPushButton:hover {
            color: white;
        }
    '''
        if button_limegreen == []:
            pass
        else:
            for button in button_limegreen:
                button.setStyleSheet(base_style + '''
                    QPushButton:hover {
                        background-color: limegreen;
                    }
                ''')
        if button_firebrick == []:
            pass
        else:
            for button in button_firebrick:
                button.setStyleSheet(base_style + '''
                    QPushButton:hover {
                        background-color: firebrick;
                    }
                ''')
        if button_darkkhaki == []:
            pass
        else:
            for button in button_darkkhaki:
                button.setStyleSheet(base_style + '''
                    QPushButton:hover {
                        background-color: darkkhaki;
                    }
                ''')
    def set_PlainText_light(self, tables):
        for table in tables:
            table.setStyleSheet('''
                QTableWidget {
                    background-color: white;
                    color: black;
                    border: 2px solid black;
                    gridline-color: gray;
                }
            
                QPlainTextEdit{
                    background-color: rgb(110, 110, 110);
                    color: white;
                    border: 1px solid black;
                }
                QLineEdit {
                    background-color: rgb(110, 110, 110);
                    color: white;
                    border: 2px solid rgb(58, 58, 58);
                    border-radius: 10px;
                    padding: 5px;
                }
                
            ''')

    def set_Table_light(self, tables):
        for table in tables:
            table.setStyleSheet('''
                QTableWidget {
                    background-color: rgb(110, 110, 110);
                    color: black;
                    border: 2px solid black;
                    gridline-color: black;
                }
            
                QPlainTextEdit{
                    background-color: black;
                    color: white;
                    border: 1px solid black;
                }
                QLineEdit {
                    background-color: rgb(110, 110, 110);
                    color: white;
                    border: 2px solid rgb(58, 58, 58);
                    border-radius: 15px;
                    padding: 5px;
                }
                
            ''')

    def dark_theme_label(self):
        
            style_mapping = {
                QtWidgets.QLabel: 'color: rgb(210, 210, 210);',
                QRadioButton: 'color: white;',
                QComboBox: 'background-color: rgb(160, 160, 160);',
                QCheckBox: 'color: white;',
                QGroupBox: 'color: white;'
            }

            text_objects = self.findChildren((QtWidgets.QLabel, QRadioButton, QComboBox, QCheckBox, QGroupBox))
            for text_object in text_objects:
                obj_type = type(text_object)
                style_sheet = style_mapping.get(obj_type)
                if style_sheet:
                    text_object.setStyleSheet(style_sheet)
    
    def dark_theme_text(self):
        excluded_labels = ['txtUserP','txtAdminP','txtDir','txtCustName','txtCustAdd','txtCustContact']
        Line_objects = self.findChildren(QtWidgets.QLineEdit)
        for Line_object in Line_objects:
            if isinstance(Line_object, QtWidgets.QLineEdit) and Line_object.objectName() not in excluded_labels:
                Line_object.setStyleSheet('background-color: rgb(190, 190, 190);')
           
        
    def light_theme_text(self):
        style_mapping = {
            QtWidgets.QLabel: 'color: black;',
            QRadioButton: 'color: black;',
            QLCDNumber: 'background-color: gray;',
            QComboBox: 'background-color: rgb(160, 160, 160);',
            QCheckBox: 'color: black;',
            QGroupBox: 'color: black;'
        }

        objects = self.findChildren((QtWidgets.QLabel, QRadioButton, QLCDNumber, QCheckBox, QGroupBox))
        for obj in objects:
            obj_type = type(obj)
            style_sheet = style_mapping.get(obj_type)
            if style_sheet:
                obj.setStyleSheet(style_sheet)
              
               
    
          


    def quantity_limiter(self):
        self.spinQ.setValue(1)
        query = f"SELECT qty FROM Products WHERE prod_id = '{self.txtID.text()}'"
        records = self.fetcher(query)
        self.spinQ.setMaximum(records[0][0])
        
    def enable_buttons(self):
        if current_user['username'] == 'admin':
            self.btnEdit.setEnabled(True)
            self.btnRemove.setEnabled(True)
            self.btnRestock.setEnabled(True)
            self.btnAddSel.setEnabled(True)
            self.btnSell.setEnabled(True)
            self.btnAdd.setEnabled(True)
        elif current_user['username'] == 'user':
            self.btnEdit.setEnabled(False)
            self.btnRemove.setEnabled(False)
            self.btnRestock.setEnabled(False)
            self.btnAddSel.setEnabled(True)
            self.btnSell.setEnabled(True)
            self.btnAdd.setEnabled(True)
    
    def disable_buttons(self):
        self.btnEdit.setEnabled(False)
        self.btnRemove.setEnabled(False)
        self.btnRestock.setEnabled(False)
        self.btnAddSel.setEnabled(False)
        self.btnSell.setEnabled(False)
        self.btnAdd.setEnabled(True)

    def change_state(self):
        self.setupTable(tblInfo_Fields_main, '', 'tblData')
        if self.btnSeeAll.isChecked():
            if self.btnBrNew.isChecked():
                self.show_table('','tblData', "SELECT prod_id, state, category, prod_name, qty, price FROM Products WHERE state = 'Brand New'")
            elif self.btnSecH.isChecked():
                self.show_table('','tblData', "SELECT prod_id, state, category, prod_name, qty, price FROM Products WHERE state = '2nd Hand'")
        elif self.btnCat.isChecked():
            self.toggle_view()

    def toggle_view(self):
        if self.btnSeeAll.isChecked():
            self.cmbCat.setEnabled(False)
            self.cmbCat.setCurrentIndex(0)
            self.change_state()
        elif self.btnCat.isChecked():
            self.cmbCat.setEnabled(True)
            State = self.CatSelect.checkedButton()
            query = f"SELECT Category FROM Category WHERE State = '{State.text()}'"
            records = self.fetcher(query)
            self.cmbCat.clear()
            for cat in range(len(records)):
                self.cmbCat.addItem(records[cat][0])
            self.cmbCat.setCurrentIndex(0)
            self.sort_table_by_category()

    def sort_table_by_category(self):
        State = self.CatSelect.checkedButton()
        self.setupTable(tblInfo_Fields_main, '', 'tblData')
        self.show_table('','tblData', f"SELECT prod_id, state, category, prod_name, qty, price FROM Products WHERE state = '{State.text()}' AND category = '{self.cmbCat.currentText()}'")

    def edit_item(self):
        try:
            self.add.txtQty.setDisabled(True)
            current_selection = self.tblData.item(self.tblData.currentRow(), 0).text()
            query = f"SELECT prod_id, prod_name, brand, model, qty, price FROM Products WHERE prod_id = '{current_selection}'"
            records = self.fetcher(query)
            for j in range(len(records[0])):
                eval('self.add.'+edit_fields[j]+'.setText(str(records[0][j]))')
            query2 = f"SELECT specs FROM Products WHERE prod_id = '{current_selection}'"
            records2 = self.fetcher(query2)
            self.add.txtSpecs.setPlainText(records2[0][0])
            query3 = f"SELECT state, category FROM Products WHERE prod_id = '{current_selection}'"
            records3 = self.fetcher(query3)
            self.add.cmbState.setCurrentText(records3[0][0])
            self.add.cmbCtgry.setCurrentText(records3[0][1])
        except:
            pass

    def show_details(self):
        try:
            current_selection = ''
            if self.tblData.currentRow() == 0 or self.tblData.item(self.tblData.currentRow(), 0) == None:
                for i in range(len(display_fields)):
                    eval('self.'+display_fields[i]+'.setText("")')
                self.txtSpecs.setPlainText("")
                self.spinQ.setEnabled(False)
                self.disable_buttons()
            else:
                current_selection = self.tblData.item(self.tblData.currentRow(), 0).text()
                query = f"SELECT prod_id, state, category, prod_name, brand, model, qty, price FROM Products WHERE prod_id = '{current_selection}'"
                records = self.fetcher(query)
                for j in range(len(records[0])):
                    eval('self.'+display_fields[j]+'.setText(str(records[0][j]))')
                query2 = f"SELECT specs FROM Products WHERE prod_id = '{current_selection}'"
                records2 = self.fetcher(query2)
                self.txtSpecs.setPlainText(records2[0][0])
                query3 = f"SELECT qty FROM Products WHERE prod_id = '{current_selection}'"
                records3 = self.fetcher(query3)
                if records3[0][0] == 0:
                    self.spinQ.setEnabled(False)
                    self.disable_buttons()
                    self.btnRestock.setEnabled(True)
                    self.btnEdit.setEnabled(True)
                    self.btnRemove.setEnabled(True)
                    self.spinQ.setValue(0)
                    self.txtNotif.setText('Out of Stock!')
                elif records3[0][0] < 3:
                    self.spinQ.setEnabled(True)
                    self.quantity_limiter()
                    self.enable_buttons()
                    self.txtNotif.setText('Minimum Stocks Left!')
                else:
                    self.spinQ.setEnabled(True)
                    self.quantity_limiter()
                    self.enable_buttons()
                    self.txtNotif.setText('')
        except:
            pass

    def add_to_selection(self):
        try:
            if self.txtID.text() == '':
                self.messages('warning', 'Error!', 'Please select an item!')
            else:
                selected_items.append(self.txtID.text())
                selected_items_name.append(self.txtName.text())
                selected_items_quantity.append(self.spinQ.value())
                selected_items_total_per_item.append(float(self.txtUP.text()))
                self.display_selection()
        except:
            pass

    def display_selection(self):
        temp_list = []
        selected = ''
        name = ''
        quantity = ''
        total = ''
        for i in range(len(selected_items)):
            selected = selected_items[i]
            name = selected_items_name[i]
            quantity = selected_items_quantity[i]
            total = selected_items_total_per_item[i]
            temp_list.append(f"{selected}: {name} x{quantity} = {total}")
        display = '\n'.join(temp_list)
        self.txtSelect.setPlainText(display)
        self.txtTotal.setText(str(sum(map(float, selected_items_total_per_item))))

    def compute_total_per_product(self):
        if self.txtID.text() == '':
            pass
        else:
            query = f"SELECT price FROM Products WHERE prod_id = '{self.txtID.text()}'"
            records = self.fetcher(query)
            unit_price = records[0][0]
            quantity = self.spinQ.value()
            total = float(unit_price) * quantity
            self.txtUP.setText(str(total))

    def remove_selections_prompt(self):
        if self.txtSelect.toPlainText() == '':
            self.messages('warning', 'Error!', 'No selections to clear!')
        else:
            self.prompt('Clear Selection', 'Are you sure you want to clear selections?', self.remove_selections, QMessageBox.Information)
    
    def remove_selections(self, main=''):
        selected_items.clear()
        selected_items_quantity.clear()
        selected_items_total_per_item.clear()
        self.txtSelect.setPlainText('')
        self.txtTotal.clear()
        if main == '':
            self.messages('information', 'Success!', 'Selections cleared!')
        else:
            pass

    def add_category_setter(self):
        query = f"SELECT category FROM Category WHERE State = '{self.add.cmbState.currentText()}'"
        records = self.fetcher(query)
        self.add.cmbCtgry.clear()
        for cat in range(len(records)):
            self.add.cmbCtgry.addItem(records[cat][0])
        
    def date_time(self):
        self.strCurrentTime = QtCore.QTime.currentTime()
        self.prt = self.strCurrentTime.toString("hh:mm:ss")
        self.strCurrentDate = self.currentDate.toString("MM.dd")
        self.update
        self.lcdDT.display(self.strCurrentDate +" " + self.prt)
        
    def add_edit_item_prompt(self):
        if self.add.lbladd_edit.text() == 'Add New Item':
            self.prompt('Add Item', 'Are you sure you want to add item?', self.add_item, QMessageBox.Information)
        else:
            self.prompt('Update Item', 'Are you sure you want to update item?', self.update_item, QMessageBox.Information)
    
    def add_item(self):
        date = datetime.today()
        self.id2 = self.add.txtProID.text()
        prod_name = self.add.txtName.text()
        query=f"INSERT INTO Products (prod_id, state, category, prod_name, brand, model, qty, specs, price) VALUES ('{self.id2}', '{self.add.cmbState.currentText()}', '{self.add.cmbCtgry.currentText()}', '{prod_name}', '{self.add.txtBrand.text()}', '{self.add.txtModel.text()}', '{self.add.txtQty.text()}', '{self.add.txtSpecs.toPlainText()}', '{self.add.txtUP.text()}')"
        if prod_name=='' or self.add.txtBrand.text()=='' or self.add.txtModel.text()=='' or self.add.txtQty.text()=='' or self.add.txtSpecs.toPlainText()=='' or self.add.txtUP.text()=='':
            self.messages('warning', 'Error!', 'Please Fill up All Fields')
        else:
            self.run_query(query)
            query1=f"INSERT INTO Used_ID (prod_id, prod_name, timestamp) VALUES ('{self.id2}', '{prod_name}', '{date}')"
            self.run_query(query1)
            self.log_action('add', product_name = prod_name, quantity = self.add.txtQty.text())
            self.messages('information', 'Success!', f'Product {prod_name} x{self.add.txtQty.text()} Added!')
            self.add.hide(), self.show()
            self.tblData.clearSelection()
            self.change_state()

    def update_item(self):
        prod_id=self.add.txtProID.text()
        query=f"UPDATE Products SET state='{self.add.cmbState.currentText()}', category='{self.add.cmbCtgry.currentText()}', prod_name='{self.add.txtName.text()}', brand='{self.add.txtBrand.text()}', model='{self.add.txtModel.text()}', specs='{self.add.txtSpecs.toPlainText()}', price='{self.add.txtUP.text()}' WHERE prod_id='{prod_id}'"
        if self.add.txtName.text()=='' or self.add.txtBrand.text()=='' or self.add.txtModel.text()=='' or self.add.txtSpecs.toPlainText()=='' or self.add.txtUP.text()=='':
            self.messages('warning', 'Error!', 'Please Fill up All Fields')
        else:
            self.run_query(query)
            self.log_action('edit', product_name = self.add.txtName.text())
            self.messages('information', 'Success!', f"Product {self.add.txtName.text()}'s details updated!")
            self.clear_fields(self.display_fields2)
            self.txtSpecs.setPlainText('')
            self.add.hide(), self.show()
            self.change_state()
        
    def remove_item(self):
        try:
            current_selection = self.tblData.item(self.tblData.currentRow(), 0).text()
            query = f"DELETE FROM Products WHERE prod_id = '{current_selection}'"
            self.run_query(query)
            self.log_action('delete', product_name=self.txtName.text())
            self.messages('information', 'Success!', f"Product {self.txtName.text()} deleted!")
            self.clear_fields(self.display_fields2)
            self.txtSpecs.setPlainText('')
            self.hide(), self.show()
            self.change_state()
        except:
            pass

    def add_category(self):
        self.cat_input, ok = QInputDialog.getText(self, "Add Category", "Enter Category Name:", QLineEdit.Normal)
        if ok:
            query = f"INSERT INTO Category (State, Category) VALUES ('{self.ctgry.cmbState.currentText()}', '{self.cat_input}')"
            self.run_query(query)
            self.messages('information', 'Success!', f'Category {self.cat_input} Added!')
            self.log_action('category', '', '', '', '', self.cat_input, self.ctgry.cmbState.currentText())
            self.showList()
        else:
            pass

    def edit_category(self):
        self.cat_edit_input, ok = QInputDialog.getText(self, "Edit Category", "Enter New Category Name:", QLineEdit.Normal)
        if ok:
            previous_category = self.ctgry.cmbCat.currentText()
            turninto = self.cat_edit_input
            query1 = f"SELECT prod_id FROM Products WHERE category = '{previous_category}' AND state = '{self.ctgry.cmbState.currentText()}'"
            records = self.fetcher(query1)
            dialog = QMessageBox.question(self, 'Edit Category', f'Are you sure you want to edit category {previous_category} name to {turninto}? \nThis will also update all the associated products with it.', QMessageBox.Ok | QMessageBox.Cancel)
            if dialog == QMessageBox.Ok:
                query = f"UPDATE Category SET Category = '{self.cat_edit_input}' WHERE Category = '{previous_category}' AND State = '{self.ctgry.cmbState.currentText()}'"
                self.run_query(query)
                for i in range(len(records)):
                    query2 = f"UPDATE Products SET category = '{turninto}' WHERE prod_id = '{records[i][0]}'"
                    self.run_query(query2)
                self.messages('information', 'Success!', f'Category {previous_category} updated to {turninto}!')
                self.log_action('category edit', category=previous_category, category_turninto=turninto)
                self.showList()
                self.btnBrNew.setChecked(True)
                self.btnSeeAll.setChecked(True)
                self.change_state()
        else:
            pass
    
    def remove_category(self):
        to_remove = self.ctgry.cmbCat.currentText()
        state = self.ctgry.cmbState.currentText()
        query = f"SELECT prod_id FROM Products WHERE category = '{to_remove}' AND state = '{state}'"
        records = self.fetcher(query)
        if len(records) > 0:
            choice = QMessageBox.question(self, 'Delete Category', f'Are you sure you want to delete category {to_remove}? \nThis will also delete all products under this category.', QMessageBox.Ok | QMessageBox.Cancel)
            if choice == QMessageBox.Ok:
                query = f"DELETE FROM Category WHERE Category = '{to_remove}' AND State = '{state}'"
                self.run_query(query)
                for i in range(len(records)):
                    query2 = f"DELETE FROM Products WHERE prod_id = '{records[i][0]}'"
                    self.run_query(query2)
                    self.log_action('category remove product', product_name=records[i][0])
                self.messages('information', 'Success!', f'Category {to_remove} Removed!')
                self.log_action('category remove', '', '', '', '', to_remove)
                self.showList()
            else:
                pass
        else:
            query = f"DELETE FROM Category WHERE Category = '{to_remove}' AND State = '{state}'"
            self.run_query(query)
            self.messages('information', 'Success!', f'Category {to_remove} Removed!')
            self.log_action('category remove', '', '', '', '', to_remove)
            self.showList()
    
    def restock_item(self):
        self.restock.txtIDres.setText(self.txtID.text())
        self.restock.txtNameres.setText(self.txtName.text())
        self.restock.txtStockres.setText(self.txtQty.text())
        self.restock.spinRes.setValue(1)
    
    def restock_qty(self):
        id= self.restock.txtIDres.text()
        qty = int(self.txtQty.text())
        qtyup = self.restock.spinRes.value()
        query = f"UPDATE Products SET qty = '{qty + qtyup}' WHERE prod_id = '{id}'"
        self.run_query(query)
        print(qtyup)
        if qtyup == 1:
            self.messages('information', 'Success!', f'{qtyup} stock of {self.restock.txtNameres.text()} Added!')
        else:
            self.messages('information', 'Success!', f'{qtyup} stocks of {self.restock.txtNameres.text()} Added!')
        self.log_action('restock', product_name=self.restock.txtNameres.text(), restock_value=qtyup)
        self.clear_fields(self.display_fields2)
        self.txtSpecs.setPlainText('')
        self.restock.hide(), self.show()
        self.change_state()

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

    def show_sales_records(self):
        self.sales_records.show()
        self.setupTable(sales_table,'sales_records','.tblSales')
        self.show_table('sales_records','.tblSales', "SELECT * from Output_Logs")

    def show_logs(self):
        self.view_logs.show()
        self.setupTable(logs_table,'view_logs','.tblLogs')
        self.show_table('view_logs','.tblLogs', "SELECT action_id,username,timestamp,action from Action_Logs")

    def show_customer_records(self):
        self.records.show()
        self.setupTable(cust_table,'records','.tblCust')
        self.show_table('records','.tblCust', "SELECT customer_id, customer_name,customer_address,customer_number from Customer_Info")    

    def search_table(self):
        search_text = self.view_logs.txtSearch.text().lower()

        # Iterate over the rows in the table
        for row in range(self.view_logs.tblLogs.rowCount()):
            # Nested for loop para masearch ung row at column pero pede rin naman row lang kaso dalawa kasi yon eh
            row_hidden = True
            for col in range(self.view_logs.tblLogs.columnCount()):
                item = self.view_logs.tblLogs.item(row+1, col)
                if item and search_text in item.text().lower():
                    row_hidden = False
                    break
            self.view_logs.tblLogs.setRowHidden(row+1, row_hidden)
            
    def search_sales_records(self):
        search = self.sales_records.txtSearch.text().lower()
        for row in range(self.sales_records.tblSales.rowCount()):
            item_checked = self.sales_records.tblSales.item(row+1, 6)
            if item_checked and search in item_checked.text().lower():
                self.sales_records.tblSales.setRowHidden(row+1, False)
            else:
                self.sales_records.tblSales.setRowHidden(row+1, True)

    def search_records(self):
        search = self.records.txtSearch.text().lower()
        for row in range(self.records.tblCust.rowCount()):
            item_checked = self.records.tblCust.item(row+1, 1)
            if item_checked and search in item_checked.text().lower():
                self.records.tblCust.setRowHidden(row+1, False)
            else:
                self.records.tblCust.setRowHidden(row+1, True)

    def date_table(self):
        selected_date = self.view_logs.DateLogs.date()
        sa=selected_date.toString('yyyy-MM-dd')

        for row in range(self.view_logs.tblLogs.rowCount()):
            item = self.view_logs.tblLogs.item(row+1, 2)
            if item is not None:
                item_date = item.text().split()[0]  # hinihiwalay ung date sa oras 
                if item_date == sa:
                    self.view_logs.tblLogs.setRowHidden(row, False)
                else:
                    self.view_logs.tblLogs.setRowHidden(row+1, True)

    def search_inventory(self):
        search = self.txtSearch.text().lower()
        for row in range(self.tblData.rowCount()):
            item_checked = self.tblData.item(row+1, 3)
            if item_checked and search in item_checked.text().lower():
                self.tblData.setRowHidden(row+1, False)
            else:
                self.tblData.setRowHidden(row+1, True)

    def check_auth(self, level):
        if level == 'admin':
            self.btnEdit.setEnabled(False)
            self.btnRemove.setEnabled(False)
            self.btnRestock.setEnabled(False)
            self.btnRemove.setEnabled(False)
            self.btnSettings.setEnabled(True)
        elif level == 'user':
            self.btnEdit.setEnabled(False)
            self.btnRemove.setEnabled(False)
            self.btnRestock.setEnabled(False)
            self.btnCtgry.setEnabled(False)
            self.btnRemove.setEnabled(False)
            self.btnSettings.setEnabled(False)

    def display_checkout(self):
        self.clear_fields(self.sell_fields,'checkout.')
        self.checkout.cmbExisting.setCurrentIndex(0)
        self.current_item = ''
        self.current_item_name = ''
        self.current_qty = ''
        self.current_price = ''
        if self.txtID.text() == '' and self.txtSelect.toPlainText() == '':
            self.messages('warning', 'Error!', 'Please select an item!')
        else:
            self.checkout.show()
            self.close()
            self.checkout.btnWalkIn.setChecked(True)
            if self.txtSelect.toPlainText() == '':
                self.current_item = self.txtID.text()
                self.current_item_name = self.txtName.text()
                self.current_qty = self.spinQ.value()
                self.current_price = self.txtUP.text()
                self.checkout.txtItems.setPlainText(f"{self.current_item}: {self.current_item_name} x{self.current_qty}")
                self.checkout.txtTotal.setText(self.current_price)
            elif self.txtSelect.toPlainText() != '':
                self.checkout.txtItems.setPlainText(self.txtSelect.toPlainText())
                self.checkout.txtTotal.setText(self.txtTotal.text())
            else:
                self.messages('warning', 'Error!', 'Error in Checkout!')
    
    def check_details_checkout(self):
        if self.checkout.btnWalkIn.isChecked():
            if self.checkout.btnNewCust.isChecked():
                if self.checkout.txtCustName.text() == '':
                    self.messages('warning', 'Error', 'Please fill up Name')
                else:
                    self.show_receipt()
            elif self.checkout.btnExisting.isChecked():
                if self.checkout.cmbExisting.currentIndex() == 0:
                    self.messages('warning', 'Error', 'Please select a customer')
                else:
                    self.show_receipt()
        elif self.checkout.btnOnline.isChecked():
            if self.checkout.btnNewCust.isChecked():
                if self.checkout.txtCustName.text() == '' or self.checkout.txtCustContact.text() == '':
                    self.messages('warning', 'Error', 'Please fill up Name and Number')
                else:
                    self.show_receipt()
            elif self.checkout.btnExisting.isChecked():
                if self.checkout.cmbExisting.currentIndex() == 0:
                    self.messages('warning', 'Error', 'Please select a customer')
                else:
                    self.show_receipt()
    
    def set_customers(self):
        self.checkout.errorlabel.setText('')
        if self.checkout.btnExisting.isChecked() == True:
            self.checkout.cmbExisting.setEnabled(True)
            self.checkout.cmbExisting.clear()
            self.checkout.cmbExisting.addItem('Select Customer')
            self.checkout.txtCustID.setText('')
            self.checkout.txtCustContact.setEnabled(False)
            self.checkout.txtCustName.setEnabled(False)
            self.checkout.txtCustAdd.setEnabled(False)
            query = f"SELECT customer_name FROM Customer_Info ORDER BY customer_name ASC"
            records = self.fetcher(query)
            for i in range(len(records)):
                self.checkout.cmbExisting.addItem(records[i][0])
        elif self.checkout.btnNewCust.isChecked() == True:
            self.checkout.cmbExisting.setEnabled(False)
            self.checkout.cmbExisting.setCurrentIndex(0)
            self.checkout.txtCustContact.setEnabled(True)
            self.checkout.txtCustName.setEnabled(True)
            self.checkout.txtCustAdd.setEnabled(True)
            self.checkout.txtCustID.setText(self.create_ID('Customer_Info', 'customer_id'))
            self.checkout.txtExistAdd.setText('')
            self.checkout.txtExistNum.setText('')
        else:
            pass

    def cmbExisting_changeIndex(self):
        self.checkout.errorlabel.setText('')
        if self.checkout.cmbExisting.currentIndex() == 0:
            self.checkout.txtCustID.setText('')
            self.checkout.txtExistAdd.setText('')
            self.checkout.txtExistNum.setText('')
        else:
            query = f"SELECT customer_id, customer_address, customer_number FROM Customer_Info WHERE customer_name = '{self.checkout.cmbExisting.currentText()}'"
            records = self.fetcher(query)
            for data in range(len(records)):
                self.checkout.txtCustID.setText(records[data][0])
                self.checkout.txtExistAdd.setText(records[data][1])
                self.checkout.txtExistNum.setText(str(records[data][2]))

    def show_receipt(self):
        temp = []
        self.receipt.show()
        self.checkout.hide()
        tr_id = self.create_ID('Output_Logs', 'trans_id')
        date_today = current.today()
        self.receipt.txtID.setText(tr_id)
        self.receipt.txtDate.setText(str(date_today))
        if self.current_item == '':
            for i in range(len(selected_items)):
                temp.append(f"{selected_items_name[i]} x{selected_items_quantity[i]}")
            self.receipt.txtItems.setPlainText('\n'.join(temp))
        elif self.current_item != '':
            self.receipt.txtItems.setPlainText(f"{self.current_item_name} x{self.current_qty}")
        self.receipt.txtPrice.setText(self.checkout.txtTotal.text())
        if self.checkout.btnExisting.isChecked():
            self.receipt.txtName.setText(self.checkout.cmbExisting.currentText())
            self.receipt.txtNum.setText(self.checkout.txtExistNum.text())
        elif self.checkout.btnNewCust.isChecked():
            self.receipt.txtName.setText(self.checkout.txtCustName.text())
            self.receipt.txtNum.setText(self.checkout.txtCustContact.text())
        
    def print_file(self):
        try:
            dialog = QMessageBox.question(self, 'Print?', "Do you want to print the receipt? Please check all details before proceeding.", QMessageBox.Yes | QMessageBox.No)
            if dialog == QMessageBox.Yes:
                parent_dir = os.path.dirname(os.path.abspath(__file__))
                folder_name = "Receipts"
                receipt_name = f'{self.receipt.txtID.text()}_{str(current.today())}.png'
                folder_path = os.path.join(parent_dir, folder_name)
                os.makedirs(folder_path, exist_ok=True)
                image_path = os.path.join(folder_path, receipt_name)
                pixmap = QPixmap(self.receipt.print_layout_2.size())
                pixmap.fill(Qt.white)
                pixmap_painter = QPainter(pixmap)
                self.receipt.print_layout_2.render(pixmap_painter)
                pixmap_painter.end()
                pixmap.save(image_path, "PNG")
                choice = QMessageBox.question(self, 'Saved!', f'Receipt saved to {folder_path}. Open the receipt?', QMessageBox.Yes | QMessageBox.No)
                if choice == QMessageBox.Yes:
                    os.startfile(image_path)
                    self.confirm_checkout()
                else:
                    self.messages('information', 'Success!', 'Recording to main screen...')
                    self.confirm_checkout()
            else:
                pass
        except:
            self.messages('warning', 'Error!', 'Error in printing receipt!')

    def continue_without_receipt(self):
        dialog = QMessageBox.question(self, 'Continue?', "Do you want to continue without printing the receipt?", QMessageBox.Yes | QMessageBox.No)
        if dialog == QMessageBox.Yes:
            self.messages('information', 'Success!', 'Returning to main screen...')
            self.confirm_checkout()
        else:
            pass

    def confirm_checkout(self):
        tr_id = self.receipt.txtID.text()
        date_today = datetime.now()
        if self.current_item == '':
            for i in range(len(selected_items)):
                query = f"INSERT into Output_Logs (trans_id, date_exec, username, prod_id, prod_name, customer_id, customer_name, qty, total_price) VALUES ('{tr_id}', '{date_today}', '{current_user['username']}', '{selected_items[i]}', '{selected_items_name[i]}', '{self.checkout.txtCustID.text()}', '{self.receipt.txtName.text()}', '{selected_items_quantity[i]}', '{selected_items_total_per_item[i]}')"
                self.run_query(query)
                query2 = f"UPDATE Products SET qty = qty - {selected_items_quantity[i]} WHERE prod_id = '{selected_items[i]}'"
                self.run_query(query2)
                self.log_action('checkout', product_name=selected_items_name[i], purchase_count=selected_items_quantity[i])
        elif self.current_item != '':
            query = f"INSERT into Output_Logs (trans_id, date_exec, username, prod_id, prod_name, customer_id, customer_name, qty, total_price) VALUES ('{tr_id}', '{date_today}', '{current_user['username']}', '{self.current_item}', '{self.current_item_name}', '{self.checkout.txtCustID.text()}', '{self.receipt.txtName.text()}', '{self.current_qty}', '{self.current_price}')"
            self.run_query(query)
            query2 = f"UPDATE Products SET qty = qty - {self.current_qty} WHERE prod_id = '{self.current_item}'"
            self.run_query(query2)
            self.log_action('checkout', product_name=self.current_item_name, purchase_count=self.current_qty, sold_to=self.receipt.txtName.text())
        self.record_customer()
        self.change_state()
        self.receipt.close()
        self.remove_selections('receipt')
        self.show()

    def record_customer(self):
        if self.checkout.btnNewCust.isChecked():
            query = f"INSERT INTO Customer_Info (customer_id, customer_name, customer_address, customer_number) VALUES ('{self.checkout.txtCustID.text()}', '{self.checkout.txtCustName.text()}', '{self.checkout.txtCustAdd.text()}', '{self.checkout.txtCustContact.text()}')"
            self.run_query(query)
        else:
            pass

    def inv_checker(self):
        query = f"SELECT prod_id, prod_name, qty FROM Products WHERE qty = 0"
        records = self.fetcher(query)
        if len(records) > 0:
            temp_list = []
            for i in range(len(records)):
                temp_list.append(f"{records[i][0]}: {records[i][1]}")
            display = '\n'.join(temp_list)
            self.messages('information', 'Out of Stock!', f"The following products are out of stock:\n{display}")
        else:
            self.messages('information', 'Well done!', 'All products are in stock!')

    def show_settings(self):
        query = "SELECT password FROM Accounts WHERE username = 'admin'"
        records = self.fetcher(query)
        password, ok = QInputDialog.getText(self, "Password", "Enter Admin Password:", QLineEdit.Password)
       
        if ok:
            if password == records[0][0]:
                self.settings.display()
                self.remove_selections_cleanup()
                self.hide()
                self.fetch_settings()
            else:
                self.messages('warning', 'Error!', 'Incorrect Password!')
        else:
            pass
            
    def fetch_settings(self):
        self.settings.errorlabel1.setText('')
        query = "SELECT * FROM Settings"
        records = self.fetcher(query)
        query2 = "SELECT password FROM Accounts"
        records2 = self.fetcher(query2)
        if records[2][1] == 'Dark':
            self.settings.chkDark.setChecked(True)
            self.current_theme = 'Dark'
        elif records[2][1] == 'Light':
            self.settings.chkLight.setChecked(True)
            self.current_theme = 'Light'
        if records[0][1] == 'True':
            self.settings.chkLocal_On.setChecked(True)
            self.local_backup_state = 'True'
            self.local_backup_directory = records[3][1]
            self.settings.txtDir.setText(self.local_backup_directory)
            self.settings.cmbDays.setCurrentText(records[1][1])
            self.backup_days = records[1][1]
            self.settings.errorlabel1.setText('')
        elif records[0][1] == 'False':
            self.settings.chkLocal_Off.setChecked(True)
            self.local_backup_state = 'False'
            self.settings.cmbDays.setCurrentText('Never')
            self.backup_days = 'False'
            self.settings.errorlabel1.setText('')
        elif records[3][1] != 'False':
            self.settings.errorlabel1.setText('')
        elif records[3][1] == 'False' and records[0][1] == 'True':
            self.settings.errorlabel1.setText('Please select a directory.')
        self.settings.txtAdminP.setText(records2[0][0])
        self.settings.txtUserP.setText(records2[1][0])
        print (self.local_backup_state, self.backup_days, self.current_theme, self.local_backup_directory)


    def password_toggle(self, txtField, button):
        if button.isChecked():
            eval('self.settings.'+ txtField+ '.setEchoMode(QLineEdit.Normal)')
            button.setIcon(QIcon("show.png"))
        else:
            eval('self.settings.'+ txtField+ '.setEchoMode(QLineEdit.Password)')
            button.setIcon(QIcon("hide.png"))
    
    def path_selector(self):
        out_dir = eg.diropenbox(default='C:/', title='Choose ouput directory for backup')
        print (out_dir)
        if out_dir == None:
            pass
        else:
            # Create output dir
            out_dir = Path(out_dir, 'Database Backup (DO NOT DELETE)')
            out_dir.mkdir(exist_ok=True)
            self.settings.txtDir.setText(str(out_dir))
            self.local_backup_directory = str(out_dir)
            self.settings.errorlabel1.setText('')

    def days_select(self):
        if self.settings.cmbDays.currentText() == 'Never':
            self.backup_days = 'False'
        else:
            self.backup_days = self.settings.cmbDays.currentText()

    def LBToggle_onToggle(self):
        if self.settings.chkLocal_On.isChecked():
            self.settings.btnBrowse.setEnabled(True)
            self.settings.cmbDays.setEnabled(True)
            self.settings.btnImport.setEnabled(True)
            self.settings.btnExport.setEnabled(True)
            self.local_backup_state = 'True'
            self.days_select()
            if self.settings.txtDir.text() == '':
                self.settings.errorlabel1.setText('Please select a directory.')
            else:
                self.settings.errorlabel1.setText('')
        elif self.settings.chkLocal_Off.isChecked():
            self.settings.btnBrowse.setEnabled(False)
            self.settings.txtDir.setText('')
            self.settings.errorlabel1.setText('')
            self.backup_days = 'False'
            self.local_backup_directory = 'False'
            self.settings.cmbDays.setCurrentIndex(0)
            self.settings.cmbDays.setEnabled(False)
            self.settings.btnImport.setEnabled(False)
            self.settings.btnExport.setEnabled(False)

    def theme_toggle(self):
        if self.settings.chkDark.isChecked():
            self.current_theme = 'Dark'
        elif self.settings.chkLight.isChecked():
            self.current_theme = 'Light'

    def apply_settings(self):
        for_query = [self.local_backup_state, self.backup_days, self.current_theme, self.local_backup_directory]
        for_db = ['local_backup', 'auto_backup', 'theme', 'backup_directory']
        query = "SELECT * FROM Settings"
        records = self.fetcher(query)
        query2 = "SELECT password FROM Accounts"
        records2 = self.fetcher(query2)
        if self.local_backup_state != records[0][1] or self.backup_days != records[1][1] or self.current_theme != records[2][1] or self.settings.txtDir.text() != records[3][1] or self.settings.txtAdminP.text() != records2[0][0] or self.settings.txtUserP.text() != records2[1][0]:
            confirmation = QMessageBox.question(self, 'Apply Changes?', "Are you sure you want to apply changes?", QMessageBox.Yes | QMessageBox.No)
            if confirmation == QMessageBox.Yes:
                for i in range(len(for_query)):
                    query = f"UPDATE Settings SET Value = '{for_query[i]}' WHERE Setting = '{for_db[i]}'"
                    self.run_query(query)
                query2 = f"UPDATE Accounts SET password = '{self.settings.txtAdminP.text()}' WHERE username = 'admin'"
                self.run_query(query2)
                query3 = f"UPDATE Accounts SET password = '{self.settings.txtUserP.text()}' WHERE username = 'user'"
                self.run_query(query3)
                query4 = "SELECT * FROM Auto_backup_history"
                records4 = self.fetcher(query4)
                if self.backup_days == 'False':
                    pass
                else:
                    if len(records4) == 0:
                        query6 = f"INSERT INTO Auto_backup_history (month, day, year) VALUES ('{datetime.now().month}', '{datetime.now().day}', '{datetime.now().year}')"
                        self.run_query(query6)
                    else:
                        if records4[-1][0] == datetime.now().month and records4[-1][1] == datetime.now().day and records4[-1][2] == datetime.now().year:
                            pass
                        else:
                            query5 = f"INSERT INTO Auto_backup_history (month, day, year) VALUES ('{datetime.now().month}', '{datetime.now().day}', '{datetime.now().year}')"
                            self.run_query(query5)
                self.messages('information', 'Success!', 'Changes applied!')
                self.settings.close()
                self.show()
            else:
                pass
        else:
            self.messages('information', 'Notice', 'No changes applied.')

    def manual_backup(self):
        question = QMessageBox.question(self, 'Backup Data?', "Are you sure you want to backup data?", QMessageBox.Yes | QMessageBox.No)
        if question == QMessageBox.Yes:
            backup = self.backup_data()
            if backup == True:
                self.messages('information', 'Success!', f'Data has been backuped to {self.dst_dir}')
            else:
                pass
        else:
            pass

    def backup_data(self):
        try:
            query = "SELECT Value FROM Settings WHERE Setting = 'backup_directory'"
            records = self.fetcher(query)
            timestamp = datetime.now()
            src_file = "maxpc.db"
            self.dst_dir = f'{records[0][0]}\maxpc_backup_{timestamp.strftime("%Y-%m-%d_%H-%M-%S")}.db'
            shutil.copy(src_file, self.dst_dir)
            self.log_action('backup')
            return True
        except FileNotFoundError:
            self.messages('warning', 'Error!', 'There was an error during the backup process. Please check your backup directory in settings.')
            self.settings.close()
            self.show_settings()
            return False

    def restore_data(self):
        query = f"SELECT password FROM Accounts"
        records = self.fetcher(query)
        admin_password = records[0][0]
        user_password = records[1][0]
        question = QMessageBox.question(self, 'Restore Data?', "Are you sure you want to restore data? This action will overwrite your existing data.\nIt is advised to create a backup file of current data for safety purposes. Proceed with caution.\n\nPasswords will not be included during the restore.", QMessageBox.Yes | QMessageBox.No)
        if question == QMessageBox.Yes:
            file = eg.fileopenbox(title="Select data to restore", default="*.db", filetypes="*.db")
            if file == None or file == '':
                pass
            else:
                check = str(file)
                check [-2:]
                if check[-2:] != 'db':
                    self.messages('warning', 'Error!', 'Please select a valid database file.')
                else:
                    shutil.copy(file, "maxpc.db")
                    query = f"UPDATE Accounts SET password = '{admin_password}' WHERE username = 'admin'"
                    self.run_query(query)
                    query2 = f"UPDATE Accounts SET password = '{user_password}' WHERE username = 'user'"
                    self.run_query(query2)
                    self.messages('information', 'Success!', 'Data has been restored and overwriten!')
                    self.settings.close()
                    self.show()
        else:
            pass

    def auto_backup(self):
        query = "SELECT Value FROM Settings WHERE Setting = 'auto_backup'"
        records = self.fetcher(query)
        query2 = "SELECT * FROM Auto_backup_history"
        records2 = self.fetcher(query2)
        if records[0][0] == 'False':
            pass
        else:
            existing_year = []
            existing_month = []
            existing_day = []
            current_month = datetime.now().month
            current_year = datetime.now().year
            current_day = datetime.now().day
            for i in range(len(records2)):
                existing_year.append(records2[i][2])
                existing_month.append(records2[i][0])
                existing_day.append(records2[i][1])

            if len(existing_year) == 0 or len(existing_month) == 0 or len(existing_day) == 0:
                pass
            else:
                last_backup = datetime(existing_year[-1], existing_month[-1], existing_day[-1])
                date = datetime.now().date()
                compare = datetime(date.year, date.month, date.day)
                delta = last_backup + timedelta(days=int(records[0][0]))
                if compare == delta:
                    backup = self.backup_data()
                    if backup == True:
                        query = f"INSERT INTO Auto_backup_history (month, day, year) VALUES ('{current_month}', '{current_day}', '{current_year}')"
                        self.run_query(query)
                        self.notify.setText("Automatic backup done!")
                    else:
                        self.notify.setText("There was an error during the automatic backup process. Please check your backup directory in settings.")
                else:
                    pass
            
    def excel_file(self):
        try:
            # Connect to the database
            db = sqlite3.connect('maxpc.db')
            # Read data from a table in the database
            query = "SELECT trans_id AS [Transaction ID], date_exec AS Date, username AS Username, prod_id AS [Product ID], prod_name AS [Product Name], customer_id AS [Customer ID], customer_name AS [Customer Name], qty AS Quantity, total_price AS [Total Price] FROM Output_Logs"
            file = pd.read_sql_query(query, db)
            # Select the output Excel file
            save_filename, _ = QFileDialog.getSaveFileName(self, "Save Excel File", "", "Excel Files (*.xlsx)")
            
            if save_filename:
                # Save the data to Excel
                file.to_excel(save_filename, index=False)
                self.messages('information','Conversion Complete','Database converted to Excel successfully.')
            else:
                pass
        except Exception as e:
            self.messages('warning','Error',f"An error occurred during the conversion:\n\n{str(e)}")
        finally:
            # Close the database connection
            db.close()

    def week_ago(self, minus, cat, cat2):
        today = current.today()
        monday = today - timedelta(days=minus)
        if minus == 0:
            query1=f"SELECT qty, total_price FROM Output_Logs WHERE date_exec LIKE '%{today}%'"
        else:
            query1= f"SELECT qty, total_price FROM Output_Logs WHERE date_exec BETWEEN '{monday}' AND 'TODAY()'"
        records = self.fetcher(query1)
        qtys=[]
        prices=[]
        for x in range(len(records)):
            qty = records[x][0]
            price = records[x][1]
            qtys.append(qty)
            prices.append(float(price))
        tqty = (sum(qtys))
        tprice = (sum(prices))
        self.messages('information',f'{cat} Report',f'Total Products Sold This {cat2}: {tqty} \nTotal Profit: {tprice}')

    def weekly(self):
        today = current.today()
        day = today.isoweekday()
        if day == 1:
            self.week_ago(0, "Weekly", 'Week')
        elif day == 2:
            self.week_ago(1, "Weekly", 'Week')
        elif day == 3:
            self.week_ago(2, "Weekly", 'Week')
        elif day == 4:
            self.week_ago(3, "Weekly", 'Week')
        elif day == 5:
            self.week_ago(4, "Weekly", 'Week')
        elif day == 6:
            self.week_ago(5, "Weekly", 'Week')
        elif day == 7:
            self.week_ago(6, "Weekly", 'Week')

    def monthly(self):
        day = current.today().day
        day2 = day - 1
        self.week_ago(day2, "Monthly", 'Month')

    def remove_selections_cleanup(self):
        self.settings.Action_Logs.setChecked(False)
        self.settings.Output_Logs.setChecked(False)
        self.settings.Customer_Info.setChecked(False)
        self.settings.Auto_backup_history.setChecked(False)
        self.settings.btnClean.setEnabled(False)

    def data_cleanup_select(self):
        self.data_table = ['Action_Logs', 'Output_Logs', 'Customer_Info', 'Auto_backup_history']
        self.to_clean = []
        for button in range(len(self.data_table)):
            if eval('self.settings.'+ self.data_table[button]+ '.isChecked()'):
                self.to_clean.append(self.data_table[button])
            else:
                pass
        if len(self.to_clean) == 0:
            self.settings.btnClean.setEnabled(False)
        else:
            self.settings.btnClean.setEnabled(True)
        
    def proceed_cleanup(self):
        dialog = QMessageBox.question(self, 'Clean up?', "Are you sure you want to clean up the selected data? \nPlease make sure to backup your data first.", QMessageBox.Yes | QMessageBox.No)
        if dialog == QMessageBox.Yes:
            query = f"SELECT password FROM Accounts"
            records = self.fetcher(query)
            password = QInputDialog.getText(self, "Password", "Enter Admin Password:", QLineEdit.Password)
            if password[0] == records[0][0]:
                for i in range(len(self.to_clean)):
                    query = f"DELETE FROM {self.to_clean[i]}"
                    self.run_query(query)
                    self.log_action('cleanup', forclean= self.to_clean[i])
                self.messages('information', 'Success!', 'Selected data has been cleaned up!')
                self.remove_selections_cleanup()
            elif password ==  ('', False):
                pass
            else:
                self.messages('warning', 'Error!', 'Incorrect Password!')
        else:
            pass

app = QtWidgets.QApplication(sys.argv)
splash = LogIn()
splash.show()
app.exec_()