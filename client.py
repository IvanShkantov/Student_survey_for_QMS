import asyncio
import socket
import atexit
import sys

from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QGridLayout, QApplication
from PyQt5.QtCore import QCoreApplication, Qt

from Student import Student
from Admin import Admin

from PyQt5.QtGui import QFont
import qasync

from config import window_bg, PORT
from custom_widgets import CustomLabel, Message, CustomFrame, Image, ExitButton
from static_functions import add_style

# Класс Окна подключения к серверу
class ConnectionScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Подключение к серверу")

        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignTop)

        self.sock = None

        self.setLayout(self.layout)

        font = QFont("Calibri", 15)
        font.setBold(True)
        add_style(CustomLabel(self, "Введите адрес сервера", font=font), "margin-bottom: 10")

        self.address_entry = QtWidgets.QLineEdit(self)
        self.address_entry.setFont(QtGui.QFont("Source Sans Pro", 15))
        self.address_entry.setAlignment(Qt.AlignCenter)
        self.address_entry.setText("127.0.0.1")
        self.address_entry.setStyleSheet("padding:5; border-radius:25; border: 4px inset #90ada4;")

        self.layout.addWidget(self.address_entry)

        button = QPushButton("Подключиться")
        button.setObjectName("button")
        button.setStyleSheet("#button{padding: 15; border: 3 inset gray;} #button:hover{background-color: #dbdbdb; padding: 15; border: 3 inset gray;}")
        button.setFont(QFont("Bahnschrift", 15))
        button.clicked.connect(lambda : self.click(self.address_entry.text()))

        self.layout.addWidget(button)

    def click(self, host):
        async def connect():    # Попытка подключения к серверу
            success = await self.connect_to_server_async(host, PORT)
            if success:     # Успешное подключение
                self.close()
                self.main_window = Client(self.sock)
                self.main_window.show()

        asyncio.create_task(connect())

    # Асинхронное подключение к серверу
    async def connect_to_server_async(self, host, port):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.setblocking(False)
            await asyncio.get_event_loop().sock_connect(self.sock, (host, port))

            return True
        except Exception as e:
            Message("ERROR", f"Ошибка подключения: {e}",'c')
            if self.sock is not None:
                self.sock.close()
                self.sock = None
            return False

# Класс Клиент - окно для выбора роли
class Client(QMainWindow):
    def __init__(self, sock):
        super().__init__()

        self.setWindowTitle("Анкетирование студентов для СМК")
        self.resize(700, 500)

        self.sock = sock
        self.loop = asyncio.get_event_loop()

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        main_layout = QGridLayout()
        self.central_widget.layout = main_layout
        self.central_widget.setLayout(main_layout)
        self.central_widget.setObjectName("back_color")
        self.central_widget.setStyleSheet("#back_color{background-color: " + window_bg + ";}")

        self.active_widget = None

        self.role = None

        def end():
            self.sock.close()

        atexit.register(end)

        self.setup_ui()

    # Установление интерфейса
    def setup_ui(self):
        self.showNormal()

        QCoreApplication.processEvents()

        self.active_widget = CustomFrame(self.central_widget, QVBoxLayout)

        CustomLabel(self.active_widget, f"«Анкетирование студентов для СМК»"
                                        f"\nДобро пожаловать!",
                    font=QFont("Times New Roman", 30), size=(1,1))

        CustomLabel(self.active_widget, f"Выберите вашу роль:",
                    font=QFont("Times New Roman", 30), size=(1,1))

        buttons = CustomFrame(self.active_widget, QHBoxLayout, size=(1,1))
        buttons.layout.setSpacing(20)

        butt_frame = CustomFrame(buttons, QVBoxLayout, size=(0, 0))
        butt_frame.setObjectName("this")
        butt_frame.setStyleSheet("#this{background-color: lightgreen; border-radius:30; border: 4px inset #90ada4;}")
        butt_frame.setFixedWidth(384)
        add_style(butt_frame, "padding: 10;")
        Image(butt_frame, f"Студенты.png", 364, 260, 300, 220)
        label = CustomLabel(butt_frame, "Студент", size=(1, 0), font=QFont("Bahnschrift SemiBold", 20))
        label.setStyleSheet("margin: 0,10,0,0;")
        butt_frame.mousePressEvent = lambda e: self.set_role("Студент")

        butt_frame = CustomFrame(buttons, QVBoxLayout, size=(0, 0), bg="lightgreen")
        butt_frame.setObjectName("this")
        butt_frame.setStyleSheet("#this{background-color: lightgreen; border-radius:30; border: 4px inset #90ada4;}")
        butt_frame.setFixedWidth(384)
        add_style(butt_frame, "padding: 10;")
        Image(butt_frame, f"Администратор.png", 364, 260, 290, 230)
        label = CustomLabel(butt_frame, "Администратор", size=(1, 0), font=QFont("Bahnschrift SemiBold", 20))
        label.setStyleSheet("margin: 0,10,0,0;")
        butt_frame.mousePressEvent = lambda e: self.set_role("Администратор")

        row = CustomFrame(self.active_widget, QHBoxLayout, size=(1,1))

        ExitButton(row)

        QCoreApplication.processEvents()
        self.showNormal()
        self.setGeometry(904, 412, 1142, 812)

    # Установление роли, создание одного из объектов Студент или Администратор
    def set_role(self, role):
        self.active_widget.deleteLater()

        if role == "Студент":
            self.role = Student(self.sock, self.loop,
                                self.central_widget, (1026, 525, 1102, 618), self.setup_ui,
                                self)
        elif role == "Администратор":
            self.role = Admin(self.sock, self.loop,
                              self.central_widget, (694, 115, 1528, 1405), self.setup_ui,
                              self)

# Начало программы
if __name__ == "__main__":
    app = QApplication(sys.argv)

    loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(loop)

    ConnectionScreen().show()

    with loop:
        loop.run_forever()