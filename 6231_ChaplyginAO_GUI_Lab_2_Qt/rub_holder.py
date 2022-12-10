from PyQt5.QtCore import pyqtSignal, QObject
import numpy as np

class rubHolder(QObject):
    update_signal = pyqtSignal(float,float)

    def __init__(self):
        super().__init__()
        self.value = ''

    def update_value(self, k_value: float, money: float):
        #print(f'rub hi: k_value={k_value} money={money}')
        self.value = str(money * k_value)
        #print(f'rub self.value={self.value}')