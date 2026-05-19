import base64
from io import BytesIO

from PyQt5.QtGui import QPixmap, QIcon

import os

from PyQt5 import QtGui, QtWidgets
from PyQt5.QtWidgets import QSizePolicy, QApplication
from PyQt5.QtCore import Qt
from openpyxl.reader.excel import load_workbook

from static_functions import custom_settings
messagebox_icons = {'q': QtWidgets.QMessageBox.Question, 'i': QtWidgets.QMessageBox.Information, 'w': QtWidgets.QMessageBox.Warning, 'c': QtWidgets.QMessageBox.Critical}

# Класс Настраиваемый контейнер
class CustomFrame(QtWidgets.QFrame):
    def __init__(self, root, layout, bg=None, place=None, size=None):
        super().__init__(root)
        self.layout = layout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        custom_settings(self, root, place, size, bg)

    def fix_height(self):
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    def expand_height(self):
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

# Класс Пользовательская прокручивающаяся область
class CustomScrollArea(QtWidgets.QScrollArea):
    def __init__(self, root, alignment, bg=None, place=None, vert_scroll=False, horiz_scroll=False):
        super().__init__(root)
        self.setWidgetResizable(True)
        if not vert_scroll:
            self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        if not horiz_scroll:
            self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.elements = QtWidgets.QWidget()
        self.setWidget(self.elements)

        if bg is not None:
            self.elements.setStyleSheet(f"background-color: {bg};")

        if alignment == 'v':
            self.layout = QtWidgets.QVBoxLayout(self.elements)
            self.layout.setAlignment(Qt.AlignTop)
        elif alignment == 'h':
            self.layout = QtWidgets.QHBoxLayout(self.elements)
            self.layout.setAlignment(Qt.AlignLeft)

        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(1)
        self.elements.setLayout(self.layout)

        if place is None:
            root.layout.addWidget(self)
        elif len(place) == 1:
            root.layout.insertWidget(place[0], self)
        elif len(place) == 4:
            root.layout.addWidget(self, place[0], place[1], place[2], place[3])

# Класс Пользовательская надпись
class CustomLabel(QtWidgets.QLabel):
    def __init__(self, root, text="", place=None, size=None, bg=None, color="black", align=Qt.AlignCenter, font=QtGui.QFont("Calibri", 15)):
        super().__init__(text, root)
        self.setAlignment(align)
        self.setFont(font)
        self.setStyleSheet(f"color: {color};")

        custom_settings(self, root, place, size, bg)

# Класс Пользовательская надпись
class CustomEntry(QtWidgets.QLineEdit):
    def __init__(self, root, text="", place=None, size=None, bg=None, align=Qt.AlignLeft, font=QtGui.QFont("Source Sans Pro", 15)):
        super().__init__(root)
        self.setAlignment(align)
        self.setPlaceholderText(text)
        self.setFont(font)
        self.setStyleSheet(f"padding:15; border-radius:30; border: 4px inset #90ada4; margin-bottom: 30px;")

        custom_settings(self, root, place, size, bg)

# Класс Пользовательский Выпадающий список
class CustomCombobox(QtWidgets.QComboBox):
    def __init__(self, root, items, border="#58b094"):
        super().__init__(root)
        self.setFont(QtGui.QFont("Bahnschrift", 15))
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setStyleSheet(f"padding:5; margin: 5; border-radius:10; border: 4px inset {border};")
        self.addItems(items)
        root.layout.addWidget(self)

# Класс Пользовательская кнопка
# class CustomButton(CustomLabel):
#     def __init__(self, root, text, func, place=None, size=None, bg=None, color="black", align=Qt.AlignCenter, font=QtGui.QFont("Calibri", 15)):
#         super().__init__(root, text, place, size, bg, color, align, font)
#         self.cl = func

class CustomButton(QtWidgets.QPushButton):
    def __init__(self, root, text, func, place=None, size=None, bg=None, color="black", align=Qt.AlignCenter, font=QtGui.QFont("Calibri", 15)):
        super().__init__(text, root)
        # self.setAlignment(align)
        self.setFont(font)
        self.setStyleSheet(f"padding:15; border-radius:30; border: 4px inset #90ada4; color: {color}; background-color: lightgreen;")
        #
        custom_settings(self, root, place, size, bg)

        self.clicked.connect(func)

class CategoryButton(QtWidgets.QPushButton):
    def __init__(self, root, text, func, place=None, size=None, bg=None, color="black", align=Qt.AlignCenter, font=QtGui.QFont("Calibri", 15)):
        super().__init__(text, root)
        # self.setAlignment(align)
        # super().setFont(font)
        self.setFixedHeight(300)
        self.setStyleSheet(f"padding:15; border-radius:30; color: {color}; background-color: yellow;")
        #
        custom_settings(self, root, place, size, bg)

        self.clicked.connect(func)

# Класс Картинка
class Image(CustomLabel):
    def __init__(self, root, path, width, height, image_w = None, image_h = None, place=None):
        super().__init__(root, place=place)
        image_path = os.path.join(os.path.dirname(__file__), 'images', path)

        picture = QPixmap(image_path)

        self.setFixedSize(width, height)
        self.setPixmap(picture.scaled(width if image_w is None else image_w, height if image_h is None else image_h))


class ChooseYN(QtWidgets.QMessageBox):
    def __init__(self, title, text, icon='q', info=None):
        super().__init__()
        self.setIcon(messagebox_icons[icon])
        self.setWindowTitle(title)
        self.setText(text)
        if info is not None:
            self.setInformativeText(info)
        self.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)

        self.result = self.exec_() == QtWidgets.QMessageBox.Yes

class Message(QtWidgets.QMessageBox):
    def __init__(self, title, text, icon='c', info=None):
        super().__init__()
        self.setIcon(messagebox_icons[icon])
        self.setWindowTitle(title)
        self.setText(text)
        if info is not None:
            self.setInformativeText(info)
        self.setStandardButtons(QtWidgets.QMessageBox.Ok)

        self.exec_()

class ExitButton(CustomFrame):
    def __init__(self, root, place=None):
        super().__init__(root, QtWidgets.QHBoxLayout, size=(0, 0), place=place)
        self.layout.setSpacing(30)
        self.setObjectName("button")
        self.setStyleSheet("#button{background-color: #e38d8d; border: 5 inset #ad3d3d; padding-left: 20; padding-right: 20; border-radius: 30;}")
        CustomLabel(self, "Выход", font=QtGui.QFont("Calibri", 15))
        Image(self, "exit.png", 50, 50)
        self.setFixedSize(220,80)

        self.mousePressEvent = lambda e: QApplication.exit()

# Преобразование байт в Excel документ и сохранение на устройство
def save_excel(excel_base64, faculty):
    excel_bytes = base64.b64decode(excel_base64)

    wb = load_workbook(BytesIO(excel_bytes))
    try:
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(None, "Экспортировать результаты",
                                                             f"Итоги анкетирования {faculty}",
                                                             "Excel Files (*.xlsx);;All Files (*)")
        if file_path != "":
            if not file_path.endswith(".xlsx"):
                file_path += ".xlsx"
            wb.save(file_path)
            if ChooseYN("Файл сохранён",
                        "Файл сохранён успешно", 'q',
                        f"Желаете открыть?").result:
                os.startfile(file_path)
    except Exception as ex:
        Message("Ошибка", f"{ex}", 'c')