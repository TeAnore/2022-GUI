from PyQt5.QtCore import pyqtSignal, QObject
import numpy as np

class usdHolder(QObject):
    update_signal = pyqtSignal(float,float)

    def __init__(self):
        super().__init__()
        self.value = ''

    def update_value(self, k_value: float, money: float):
        #print(f'usd hi: k_value={k_value} money={money}')
        self.value = str(money / k_value)
        #print(f'usd self.value={self.value}')