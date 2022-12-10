'''
TASK
Реализовать приложение на PyQt с использованием сигнал-слот взаимодействия.

Например, приложение генератор курсов валют на торговом рынке,
хранящий три связанных курса: рубль – доллар и котировку текущей стоимости нефти.

При увеличении стоимости нефти рубль увеличивает стоимость => посылается сигнал «классу «рубля»».
При уменьшении стоимости нефти доллар увеличивает стоимость => посылается сигнал «классу «доллара»».

Курсы доллара и рубля связаны между собой коэффициентом и изменяются, например, 2, любой.

Все изменения делать при нажатии на кнопку анализ.
'''
import sys
from PyQt5 import QtWidgets

from PyQt5.QtCore import QRect, pyqtSignal, QObject
from PyQt5.QtWidgets import QApplication, QPushButton, QLineEdit, QLabel, QMessageBox
import numpy as np

WINDOW_WIDTH = 360
WINDOW_HEIGHT = 200


class MoneyStateSignal(QObject):
    update_signal = pyqtSignal(float,float)


class usdHolder:
    def __init__(self):
        super().__init__()
        self.value = ''

    def update_value(self, k_value: float, money: float):
        print(f'usd hi: k_value={k_value} money={money}')
        self.value = str(money / k_value)
        print(f'usd self.value={self.value}')


class rubHolder:
    def __init__(self):
        super().__init__()
        self.value = ''

    def update_value(self, k_value: float, money: float):
        print(f'rub hi: k_value={k_value} money={money}')
        self.value = str(money * k_value)
        print(f'rub self.value={self.value}')


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.k = 2
        self.rur = 1
        self.usd = self.rur / self.k
        self.oil = 1

        self.setFixedSize(WINDOW_WIDTH, WINDOW_HEIGHT)

        self.rubHolder = rubHolder()
        self.usdHolder = usdHolder()
        self.rubStateSignal = MoneyStateSignal()
        self.usdStateSignal = MoneyStateSignal()

        self.kLabel = QLabel(self)
        self.kLabel.setText("Коэффициент")
        self.kLabel.setGeometry(QRect(10, 10, 150, 25))
        self.kLineEdit = QLineEdit(self)
        self.kLineEdit.setGeometry(QRect(100, 10, 240, 25))

        self.oilLabel = QLabel(self)
        self.oilLabel.setText("Нефть")
        self.oilLabel.setGeometry(QRect(10, 40, 150, 25))
        self.oilLineEdit = QLineEdit(self)
        self.oilLineEdit.setGeometry(QRect(100, 40, 240, 25))

        self.rubLabel = QLabel(self)
        self.rubLabel.setText("Рубль")
        self.rubLabel.setGeometry(QRect(10, 70, 150, 25))
        self.rubLineEdit = QLineEdit(self)
        self.rubLineEdit.setGeometry(QRect(100, 70, 240, 25))
        self.rubLineEdit.setReadOnly(True)

        self.usdLabel = QLabel(self)
        self.usdLabel.setText("Доллар")
        self.usdLabel.setGeometry(QRect(10, 100, 150, 25))
        self.usdLineEdit = QLineEdit(self)
        self.usdLineEdit.setGeometry(QRect(100, 100, 240, 25))
        self.usdLineEdit.setReadOnly(True)

        self.convertButton = QPushButton(self)
        self.convertButton.setText("Расчитать курс валют")
        self.convertButton.setGeometry(QRect(80, 140, 200, 50))

        self.kLineEdit.setText(str(self.k))
        self.oilLineEdit.setText(str(self.oil))
        self.rubLineEdit.setText(str(self.rur))
        self.usdLineEdit.setText(str(self.usd))

        self.rubStateSignal.update_signal.connect(self.rubHolder.update_value)
        self.usdStateSignal.update_signal.connect(self.usdHolder.update_value)

        self.convertButton.clicked.connect(self.on_convert_button_click)

        self.show()

    def on_convert_button_click(self):
        curr_oil = float(self.oil)
        
        k_value = self.str_val_convert_to_float(self.kLineEdit.text())
        oil_value = self.str_val_convert_to_float(self.oilLineEdit.text())

        rub_value = self.str_val_convert_to_float(self.rubLineEdit.text())
        usd_value = self.str_val_convert_to_float(self.usdLineEdit.text())

        #self.rubHolder.update_signal.emit(k_value, oil_value)
        #self.usdHolder.update_signal.emit(k_value, oil_value)
    
        if curr_oil < oil_value:
            self.usdStateSignal.update_signal.emit(k_value, rub_value)
            self.usdLineEdit.setText(self.usdHolder.value)
            self.rubLineEdit.setText(str(rub_value + oil_value))
        elif curr_oil > oil_value:
            self.rubStateSignal.update_signal.emit(k_value, usd_value)
            self.rubLineEdit.setText(self.usdHolder.value)
            self.usdLineEdit.setText(str(usd_value + oil_value))
        else:
            oil_value = curr_oil

        self.oil = float(oil_value)

    def str_val_convert_to_float(self, val: str):
        
        if val is None or len(val) == 0:
            value = 0
        else:
            value = float(val)

        return value

if __name__ == '__main__':
    application = QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(application.exec_())