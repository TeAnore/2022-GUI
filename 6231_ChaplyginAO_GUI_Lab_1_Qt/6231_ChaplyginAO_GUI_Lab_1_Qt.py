from PyQt6.QtWidgets import QPushButton, QApplication, QMainWindow, QLabel, QLineEdit, QVBoxLayout, QWidget
import sys

# Группа 6231 - Чаплыгин Алексей

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Lab 1")

        button = QPushButton("Лучшая кнопка в мире!")
        button.setCheckable(True)
        button.clicked.connect(self.the_button_was_clicked)
      
        self.label = QLabel()
        layout = QVBoxLayout()
        layout.addWidget(button)
        layout.addWidget(self.label)

        container = QWidget()
        container.setLayout(layout)

        self.setCentralWidget(container)

    def the_button_was_clicked(self):
        self.label.setText('Привет Мир!')


app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()