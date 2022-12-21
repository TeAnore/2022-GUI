'''
TASK
Реализовать приложение на PyQt с использованием представления таблиц и работы с SQL.

В меню две вкладки: Set connection (установить соединение с бд), Close connection (очистить все, закрыть соединение с бд).
По умолчанию можно сделать в QTabWidget вкладки пустыми, либо создавать их по выполнению запросов при нажатии на функциональные клавиши.
Сразу после успешного коннета в Tab1 устанавливается таблица, соответствующая запросу «SELECT * FROM sqlite_master».
Кнопка bt1 делает выборочный запрос, например, «SELECT name FROM sqlite_master», результат выводится в Tab2.
При выборе колонки из выпадающего списка QComboBox результат соотвествующего запроса отправляется в Tab3.
Кнопки bt2 и bt3 выполняют запрос по выводу таблицы в Tab4 и Tab5
'''
import os
import sys
import PyQt6

import traceback

from PyQt6.QtCore import QSettings, QFileInfo, QFile, QIODevice, QIODeviceBase, QThread, Qt
from PyQt6.QtSql import *
from PyQt6.QtWidgets import QApplication, QMainWindow, QMenuBar, QStatusBar, QWidget, QPushButton, QLabel, QLineEdit, QComboBox, QTabWidget, QGridLayout, QHBoxLayout, QVBoxLayout, QTableView, QTableWidget, QHeaderView, QTableWidgetItem
from PyQt6.QtGui import QPalette, QColor

from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

from sqlalchemy import Column, Integer, String
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# WINDOW PARAMS
MIN_WINDOW_WIDTH = 842
MIN_WINDOW_HEIGHT= 420
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = '6231_ChaplyginAO_GUI_Lab_3_Qt'
DB_STATUS = 'Состояние подключения к БД: '
DB = os.path.join(os.path.dirname(__file__), 'GUI_LABS.db')

class T_LAB3(Base):
    __tablename__ = 'T_LAB3'
    id = Column(Integer, primary_key=True)
    name = Column(String(12))
    hex = Column(String(12))
    rgb = Column(String(12))
    hcv = Column(String(12))

    def init(self, id, name, hex, rgb, hcv):
        self.id = id
        self.name = name
        self.hex = hex
        self.rgb = rgb
        self.hcv = hcv

    def repr(self):
        return "<Colors('%s', '%s', '%s', '%s', '%s')>" % (self.id, self.name, self.hex, self.rgb, self.hcv)

class QueryRunner(QThread):
    def __init__(self, query, parent=None):
        super(QueryRunner, self).__init__(parent)
        self.query = query
        return 
    
    def run(self):
        self.query.exec()

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.setWindowTitle(WINDOW_TITLE)
        self.setMinimumWidth(MIN_WINDOW_WIDTH)
        self.setMinimumHeight(MIN_WINDOW_HEIGHT)
        self.setBaseSize(WINDOW_WIDTH, WINDOW_HEIGHT)

        # Main Menu Widget
        self.main_menu = QMenuBar()
        self.setMenuBar(self.main_menu)
        # FILE SubMenu
        m = self.main_menu.addMenu("Файл")
        self.exit_action = m.addAction("Выход")
        # DB SubMenu
        m = self.main_menu.addMenu("База данных")
        self.set_connetcion_action = m.addAction("Подключиться")
        self.close_connetcion_action = m.addAction("Отключиться")
        self.close_connetcion_action.setEnabled(False)
        
        # Main Menu Action
        self.exit_action.triggered.connect(self.exit_app)
        self.set_connetcion_action.triggered.connect(self.connect_db)
        self.close_connetcion_action.triggered.connect(self.disconnect_db)

        # Main Window Widget 
        self.main_widget = QWidget()
        # Main Window Layouts
        self.grid_layout = QGridLayout()
        self.hbox_layout = QHBoxLayout()
        self.vbox_layout = QVBoxLayout()

        # Query Buttons
        self.query1_button = QPushButton()
        self.query3_button = QPushButton()
        self.query4_button = QPushButton()
        
        self.query1_button.setText("Получить названия цветов")
        self.query3_button.setText("Получить значения rgb")
        self.query4_button.setText("Получить значения hex")

        self.query1_button.setEnabled(False)
        self.query3_button.setEnabled(False)
        self.query4_button.setEnabled(False)
    
        # Query Buttons Action
        self.query1_button.clicked.connect(self.get_name)
        self.query3_button.clicked.connect(self.get_rgb)
        self.query4_button.clicked.connect(self.get_hex)

        # Query Conmbo Box
        self.query2_combobox = QComboBox()
        self.query2_combobox.addItems([''])
        self.query2_combobox.setEnabled(False)

        # Query Conmbo Box Action
        self.query2_combobox.currentIndexChanged.connect(self.combobox_selection_change)

        # Tab Widget
        self.tab = QTabWidget()
        self.record_list = []

        self.is_construct = False

        self.tab_full_table = QTableWidget() 
        self.tab_full = 'Результат полной выборки &1'
        self.construct_table('FULL')

        self.tab_name_table = QTableWidget() 
        self.tab_name = 'Результат с наименованиями &2'
        self.construct_table('NAME')

        self.tab_color_table = QTableWidget() 
        self.tab_color = 'Результат с условием цвету &3'
        self.construct_table('COLOR')
        
        self.tab_rgb_table = QTableWidget() 
        self.tab_rgb = 'Результат с RGB &4'
        self.construct_table('RGB')

        self.tab_hex_table = QTableWidget() 
        self.tab_hex = 'Результат с HEX &5'
        self.construct_table('HEX')

        self.tab.setCurrentIndex(0)

        # Status Bar Widget
        self.db_state_label = QLabel()
        self.db_state_value = QLabel()
        self.status_bar = QStatusBar()
        self.status_bar.showMessage(DB_STATUS + 'Соединение отсутсвует')
    
        # Construct Layouts
        self.grid_layout.addWidget(self.query1_button, 0, 0)
        self.grid_layout.addWidget(self.query2_combobox, 0, 1)
        self.grid_layout.addWidget(self.query3_button, 1, 0)
        self.grid_layout.addWidget(self.query4_button, 1, 1)
        self.grid_layout.addWidget(self.query4_button, 1, 1)
        self.hbox_layout.addWidget(self.tab)
        
        self.vbox_layout.addItem(self.grid_layout)
        
        self.vbox_layout.addItem(self.hbox_layout)
        self.vbox_layout.addWidget(self.status_bar)

        self.main_widget.setLayout(self.vbox_layout)
        self.setCentralWidget(self.main_widget)

    def connect_db(self):
        self.is_construct = True
        self.set_connetcion_action.setEnabled(False)
        self.close_connetcion_action.setEnabled(True)
        self.query1_button.setEnabled(True)
        self.query2_combobox.setEnabled(True)
        self.query3_button.setEnabled(True)
        self.query4_button.setEnabled(True)
        self.engine = create_engine(f'sqlite:///' + DB , echo=False) 
        # Проверка существоания таблицы
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

        try:
            self.record_list = self.session.query(T_LAB3).all()
        except Exception:
            traceback.print_exc()
            return None

        items = []
        for r, data in enumerate(self.record_list):
            items += [data.name]
        
        self.query2_combobox.addItems(items)
        self.query2_combobox.setCurrentText('')
        self.query2_combobox.removeItem(self.query2_combobox.currentIndex())
        self.construct_table('FULL')
        self.is_construct = False
        self.status_bar.showMessage(DB_STATUS + 'Подключено')

    def disconnect_db(self):
        self.session.close()
        self.engine.dispose()
        self.status_bar.showMessage(DB_STATUS + 'Отсутсвует')
        self.set_connetcion_action.setEnabled(True)
        self.close_connetcion_action.setEnabled(False)
        self.query1_button.setEnabled(False)
        self.query2_combobox.setEnabled(False)
        self.query3_button.setEnabled(False)
        self.query4_button.setEnabled(False)

        while self.query2_combobox.count() > 0:
            self.query2_combobox.removeItem(0)

        self.query2_combobox.addItems([''])

        self.record_list = []
        self.construct_table('FULL')
        self.construct_table('NAME')
        self.construct_table('COLOR')
        self.construct_table('RGB')
        self.construct_table('HEX')
        
        self.tab.setCurrentIndex(0)

    def combobox_selection_change(self, i):
        if self.is_construct == False: 
            self.record_list = self.session.query(T_LAB3).filter_by(name=self.query2_combobox.currentText()).all()
            self.construct_table('COLOR')

    def get_name(self):
        if self.is_construct == False: 
            self.record_list = self.session.query(T_LAB3).all()
            self.construct_table('NAME')

    def get_rgb(self):
        if self.is_construct == False: 
            self.record_list = self.session.query(T_LAB3).all()
            self.construct_table('RGB')

    def get_hex(self):
        if self.is_construct == False: 
            self.record_list = self.session.query(T_LAB3).all()
            self.construct_table('HEX')

    def construct_table(self, type):
        header_row = []
        header_id = 0
        idx_tab = 0
        tab_description = ''

        if type == 'FULL' :
            idx_tab = 0
            tab_description = self.tab_full
            headers = ['ID', 'NAME', 'HEX', 'RGB', 'HCV']
            self.tab_full_table = QTableWidget()
            self.tab_full_table.setColumnCount(len(headers))
            for h in headers:
                header_row.append(self.tab_full_table.setHorizontalHeaderItem(header_id, QTableWidgetItem(h)))
                header_id += 1
            if len(self.record_list) > 0:
                for row_i, single_data in enumerate(self.record_list):
                    self.tab_full_table.setRowCount(self.tab_full_table.rowCount()+1)
                    self.tab_full_table.setRowHeight(self.tab_full_table.rowCount()-1, 30)
                    id = QTableWidgetItem(str(single_data.id))
                    self.tab_full_table.setItem(row_i, 0, id)
                    name = QTableWidgetItem(single_data.name)
                    self.tab_full_table.setItem(row_i, 1, name)
                    hex = QTableWidgetItem(str(single_data.hex))
                    self.tab_full_table.setItem(row_i, 2, hex)
                    rgb = QTableWidgetItem(single_data.rgb)
                    self.tab_full_table.setItem(row_i, 3, rgb)
                    hcv = QTableWidgetItem(str(single_data.hcv))
                    self.tab_full_table.setItem(row_i, 4, hcv)

            if len(self.record_list) > 0 or self.is_construct == False:
                self.tab.removeTab(idx_tab)
                self.tab.insertTab(idx_tab, self.tab_full_table, tab_description)
            else:
                self.tab.addTab(self.tab_full_table, self.tab_full)

            self.tab.setCurrentIndex(idx_tab)

        elif type == 'NAME':
            idx_tab = 1
            tab_description = self.tab_name
            headers = ['ID', 'NAME']            
            self.tab_name_table = QTableWidget()
            self.tab_name_table.setColumnCount(len(headers))
            for h in headers:
                header_row.append(self.tab_name_table.setHorizontalHeaderItem(header_id, QTableWidgetItem(h)))
                header_id += 1

            if len(self.record_list) > 0:
                for row_i, single_data in enumerate(self.record_list):
                    self.tab_name_table.setRowCount(self.tab_name_table.rowCount()+1)
                    self.tab_name_table.setRowHeight(self.tab_name_table.rowCount()-1, 30)
                    id = QTableWidgetItem(str(single_data.id))
                    self.tab_name_table.setItem(row_i, 0, id)
                    name = QTableWidgetItem(single_data.name)
                    self.tab_name_table.setItem(row_i, 1, name)

            if self.is_construct == False:
                self.tab.removeTab(idx_tab)
                self.tab.insertTab(idx_tab, self.tab_name_table, tab_description)
            else:
                self.tab.addTab(self.tab_name_table, self.tab_name)

            self.tab.setCurrentIndex(idx_tab)

        elif type == 'COLOR':
            idx_tab = 2
            tab_description = self.tab_color
            headers = ['ID', 'NAME', 'HEX', 'RGB', 'HCV']
            self.tab_color_table = QTableWidget()
            self.tab_color_table.setColumnCount(len(headers))
            for h in headers:
                header_row.append(self.tab_color_table.setHorizontalHeaderItem(header_id, QTableWidgetItem(h)))
                header_id += 1
            
            if len(self.record_list) > 0:
                for row_i, single_data in enumerate(self.record_list):
                    self.tab_color_table.setRowCount(self.tab_color_table.rowCount()+1)
                    self.tab_color_table.setRowHeight(self.tab_color_table.rowCount()-1, 30)
                    id = QTableWidgetItem(str(single_data.id))
                    self.tab_color_table.setItem(row_i, 0, id)
                    name = QTableWidgetItem(single_data.name)
                    self.tab_color_table.setItem(row_i, 1, name)
                    hex = QTableWidgetItem(str(single_data.hex))
                    self.tab_color_table.setItem(row_i, 2, hex)
                    rgb = QTableWidgetItem(single_data.rgb)
                    self.tab_color_table.setItem(row_i, 3, rgb)
                    hcv = QTableWidgetItem(str(single_data.hcv))
                    self.tab_color_table.setItem(row_i, 4, hcv)

            if self.is_construct == False:
                self.tab.removeTab(idx_tab)
                self.tab.insertTab(idx_tab, self.tab_color_table, tab_description)
            else:
                self.tab.addTab(self.tab_color_table, self.tab_color)

            self.tab.setCurrentIndex(idx_tab)

        elif type == 'RGB':
            idx_tab = 3
            tab_description = self.tab_rgb
            headers = ['ID', 'NAME', 'RGB']
            self.tab_rgb_table = QTableWidget()
            self.tab_rgb_table.setColumnCount(len(headers))
            for h in headers:
                header_row.append(self.tab_rgb_table.setHorizontalHeaderItem(header_id, QTableWidgetItem(h)))
                header_id += 1

            if len(self.record_list) > 0:
                for row_i, single_data in enumerate(self.record_list):
                    self.tab_rgb_table.setRowCount(self.tab_rgb_table.rowCount()+1)
                    self.tab_rgb_table.setRowHeight(self.tab_rgb_table.rowCount()-1, 30)
                    id = QTableWidgetItem(str(single_data.id))
                    self.tab_rgb_table.setItem(row_i, 0, id)
                    name = QTableWidgetItem(single_data.name)
                    self.tab_rgb_table.setItem(row_i, 1, name)
                    rgb = QTableWidgetItem(single_data.rgb)
                    self.tab_rgb_table.setItem(row_i, 2, rgb)

            if self.is_construct == False:
                self.tab.removeTab(idx_tab)
                self.tab.insertTab(idx_tab, self.tab_rgb_table, tab_description)
            else:
                self.tab.addTab(self.tab_rgb_table, self.tab_rgb)

            self.tab.setCurrentIndex(idx_tab)

        elif type == 'HEX':
            idx_tab = 4
            tab_description = self.tab_hex
            headers = ['ID', 'NAME', 'HEX']
            self.tab_hex_table = QTableWidget()
            self.tab_hex_table.setColumnCount(len(headers))
            for h in headers:
                header_row.append(self.tab_hex_table.setHorizontalHeaderItem(header_id, QTableWidgetItem(h)))
                header_id += 1

            if len(self.record_list) > 0:
                for row_i, single_data in enumerate(self.record_list):
                    self.tab_hex_table.setRowCount(self.tab_hex_table.rowCount()+1)
                    self.tab_rgb_table.setRowHeight(self.tab_hex_table.rowCount()-1, 30)
                    id = QTableWidgetItem(str(single_data.id))
                    self.tab_hex_table.setItem(row_i, 0, id)
                    name = QTableWidgetItem(single_data.name)
                    self.tab_hex_table.setItem(row_i, 1, name)
                    hex = QTableWidgetItem(single_data.hex)
                    self.tab_hex_table.setItem(row_i, 2, hex)

            if self.is_construct == False:
                self.tab.removeTab(idx_tab)
                self.tab.insertTab(idx_tab, self.tab_hex_table, tab_description)
            else:
                self.tab.addTab(self.tab_hex_table, self.tab_hex)

            self.tab.setCurrentIndex(idx_tab)


    def show_query_result(self):
        return

    def exit_app(self):
        application.quit()

class Color(QWidget):

    def __init__(self, color):
        super(Color, self).__init__()
        self.setAutoFillBackground(True)

        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(color))
        self.setPalette(palette)

if __name__ == '__main__':
    pyqt = os.path.dirname(PyQt6.__file__)
    QApplication.addLibraryPath(os.path.join(pyqt, "Qt", "plugins"))
    application = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(application.exec())