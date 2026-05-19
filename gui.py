import os
from datetime import date

from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QSizePolicy, QGridLayout, QButtonGroup, \
    QRadioButton, QTextEdit, QMainWindow, QWidget

from config import window_bg, faculties
from custom_widgets import CustomFrame, CustomScrollArea, CustomButton, CustomLabel, ExitButton, Image, CustomEntry
from static_functions import add_style, change_color, get_color_from_percent


# Класс анкеты студентов
class QuestionnaireForm:
    def __init__(self, parent, category, questions, close_questionnaire, send_form):
        self.widget = CustomFrame(parent, QVBoxLayout)

        area = CustomScrollArea(self.widget, 'v', vert_scroll=True)
        area.elements.setObjectName("back_color")
        area.elements.setStyleSheet("#back_color{background-color: " + window_bg + ";}")

        area.elements.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        area.layout.setSpacing(30)

        buttons_frame = CustomFrame(area, QHBoxLayout, size=(1, 0))

        back_butt = CustomButton(buttons_frame, "Назад", lambda e, c=category: close_questionnaire(c))
        back_butt.setFixedSize(200, 80)

        CustomLabel(buttons_frame, f"АНКЕТА\nОЦЕНКА УДОВЛЕТВОРЁННОСТИ {category.upper()}ОВ",
                    font=QFont("Times New Roman", 30), size=(1, 1))
        ExitButton(buttons_frame)

        faculty_chose = CustomFrame(area, QtWidgets.QHBoxLayout, size=(0, 0))
        faculty_chose.layout.setSpacing(5)

        self.error_label = CustomLabel(area, size=(1, 0))
        add_style(self.error_label, "padding: 10;")

        CustomLabel(faculty_chose, "Факультет:", font=QtGui.QFont("Source Sans Pro", 20))
        fac_combo = QtWidgets.QComboBox(faculty_chose)
        fac_combo.setFont(QtGui.QFont("Source Sans Pro", 20))
        fac_combo.setEditable(True)
        fac_combo.setFixedWidth(250)
        fac_combo.setStyleSheet("padding:5; border-radius:7; border: 4px inset #90ada4; margin-left:20;")
        fac_combo.setIconSize(QSize(40, 40))
        fac_combo.lineEdit().setFont(QtGui.QFont("Source Sans Pro", 20))
        for fac in faculties:
            image_path = os.path.join(os.path.dirname(__file__), 'images/faculty icons', f"{fac.lower()}.png")
            fac_combo.addItem(QIcon(f"{image_path}"), fac)
        fac_combo.setCurrentIndex(-1)
        faculty_chose.layout.addWidget(fac_combo)

        if category == "Студент":
            year_chose = CustomFrame(faculty_chose, QtWidgets.QHBoxLayout)
            year_chose.setStyleSheet("margin-left: 50;")
            year_chose.layout.setSpacing(20)
            CustomLabel(year_chose, "Курс:", font=QtGui.QFont("Source Sans Pro", 20))
            year_entry = QtWidgets.QLineEdit(year_chose)
            year_entry.setValidator(QtGui.QIntValidator(parent))
            year_entry.setFont(QtGui.QFont("Source Sans Pro", 20))
            year_entry.setFixedWidth(80)
            year_entry.setAlignment(Qt.AlignCenter)
            year_entry.setStyleSheet("padding:5; border-radius:7; border: 4px inset #90ada4; margin-left:20;")
            faculty_chose.layout.addWidget(year_entry)

        date_frame = CustomFrame(faculty_chose, QtWidgets.QHBoxLayout)
        date_frame.setStyleSheet("margin-left: 50;")
        date_frame.layout.setSpacing(20)
        CustomLabel(date_frame, "Дата анкетирования:", font=QtGui.QFont("Source Sans Pro", 20))
        date_entry = QtWidgets.QLineEdit(date_frame)
        date_entry.setText(date.today().strftime("%d.%m.%Y"))
        date_entry.setReadOnly(True)
        date_entry.setFont(QtGui.QFont("Source Sans Pro", 20))
        date_entry.setFixedWidth(280)
        date_entry.setAlignment(Qt.AlignCenter)
        date_entry.setStyleSheet("padding:5; border-radius:7; border: 4px inset #90ada4; margin-left:20;")
        faculty_chose.layout.addWidget(date_entry)

        text = CustomLabel(area,
                           f"1. Выберите для каждого критерия ОДИН вариант оценки (<span style='color:red;'>ОБЯЗАТЕЛЬНЫЙ ВОПРОС</span>)",
                           align=Qt.AlignLeft, size=(1, 0),
                           font=QFont("Times New Roman", 20))
        text.setWordWrap(True)
        text.setStyleSheet("margin: 20;")

        table = CustomFrame(area, QGridLayout, size=(1, 1))
        table.layout.setRowStretch(0, 2)
        table.layout.setRowStretch(1, 20)

        header_table = CustomFrame(table, QGridLayout, place=(0, 1, 1, 1))
        header_table.setObjectName("this")
        header_table.setStyleSheet("#this{padding-right:25}")

        font = QFont("Calibri", 17)
        font.setBold(True)
        header_crit = CustomLabel(table, "Критерии оценки", (0, 0, 1, 1),
                                  font=font, bg="#0be397")
        add_style(header_crit, "border-top-left-radius: 20px")  # border: 2 solid black;
        header_crit.setFixedWidth(500)

        header_variants = CustomLabel(header_table, "ВАРИАНТЫ ОЦЕНКИ", (0, 0, 1, 4), size=(1, 1),
                                      font=QFont("Calibri", 17), bg="#36d179")
        add_style(header_variants, "border-top-right-radius: 20px; padding: 10;")

        chose_headers = ["полностью удовлетворён", "скорее удовлетворён, чем не удовлетворён",
                         "скорее не удовлетворён, чем удовлетворён", "полностью не удовлетворён"]

        font = QFont("Calibri", 17)
        font.setItalic(True)
        col = 0
        for header in chose_headers:
            header_label = CustomLabel(header_table, header, (1, col, 1, 1), size=(1, 1),
                                       font=font, bg="white")
            header_label.setWordWrap(True)
            add_style(header_label, "border: 2 solid black;")
            col += 1

        area = CustomScrollArea(table, 'v', vert_scroll=True, place=(1, 0, 1, 5))
        area.verticalScrollBar().setStyleSheet("""
                                QScrollBar:vertical {
                                    width: 25px;
                                }
                            """)
        area.elements.setObjectName("back_color")
        area.elements.setStyleSheet("#back_color{background-color: " + window_bg + ";}")

        area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        area.elements.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        quest_choose = questions[0]
        quest_text = questions[1]

        button_groups = {}

        for number in range(1, len(quest_choose) + 1):
            row_box = CustomFrame(area, QHBoxLayout)
            question_label = CustomLabel(row_box, f"{number}. {quest_choose[str(number)][1]}", align=Qt.AlignLeft,
                                         font=QFont("Calibri", 17), bg="white")
            question_label.setWordWrap(True)
            add_style(question_label, "border: 2px solid black;")
            question_label.setFixedWidth(500)

            buttons = QButtonGroup()
            button_groups[quest_choose[str(number)][0]] = buttons

            cell = CustomFrame(row_box, QHBoxLayout)

            for col in range(1, 5):
                frame = CustomFrame(cell, QHBoxLayout, size=(1, 1))
                frame.setObjectName("this")
                frame.setStyleSheet("#this{background-color: #dcdcdc; padding: 10; border: 2px solid black;}")

                rb = QRadioButton(frame)
                frame.mousePressEvent = lambda e, but=rb: but.setChecked(True)

                rb.setStyleSheet("""
                            QRadioButton::indicator {
                                width: 40px;
                                height: 40px;
                            }
                        """)
                rb.isChecked()
                rb.toggled.connect(lambda e, but=rb, block=frame, color=col: change_color(but, block, color))

                rb.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
                frame.layout.addWidget(rb)
                buttons.addButton(rb, col)

        text_answers = {}

        for number in range(2, len(quest_text) + 2):
            row_box = CustomFrame(area, QVBoxLayout, size=(1, 0))
            text = CustomLabel(row_box, f"{number}. {quest_text[str(number)][1]}", align=Qt.AlignLeft, size=(1, 0),
                               font=QFont("Times New Roman", 20))
            text.setWordWrap(True)
            add_style(text, "margin: 10; padding: 10")
            textbox = QTextEdit(row_box)
            textbox.setFont(QFont("Calibri", 18))
            textbox.setStyleSheet("padding:5; border-radius:7; border: 4px inset #90ada4;")
            textbox.setFixedHeight(100)
            row_box.layout.addWidget(textbox)
            text_answers[quest_text[str(number)][0]] = textbox

        butt = CustomButton(self.widget, "Отправить",
                            lambda e, groups=button_groups, texts=text_answers:
                            send_form(category, groups, texts,
                                           fac_combo.currentText(),
                                           None if category != "Студент" else year_entry.text(),
                                           date_entry.text()),
                            font=QFont("Source Sans Pro", 20))

        add_style(butt, "padding: 20; margin: 10;")

# Класс отображения категорий администратора
class AdminCategories:
    def __init__(self, parent, categories, go_back, open_results_table, change_status):
        self.widget = CustomFrame(parent, QVBoxLayout)

        buttons_frame = CustomFrame(self.widget, QHBoxLayout, size=(1, 0))
        back_butt = CustomButton(buttons_frame, "Выйти из учётной записи", lambda: go_back())
        back_butt.setFixedSize(400, 80)
        CustomFrame(buttons_frame, QHBoxLayout, size=(1, 1))
        ExitButton(buttons_frame)

        label = CustomLabel(self.widget, f"Выберите необходимую категорию, чтобы узнать результаты анкетирования:",
                            font=QFont("Times New Roman", 25), size=(1, 0))

        label.setWordWrap(True)
        label.setStyleSheet("margin: 20,0,0,0;")

        buttons = CustomFrame(self.widget, QHBoxLayout)

        for name in categories.keys():
            frame = CustomFrame(buttons, QVBoxLayout, size=(0, 0))
            add_style(frame, "padding-top: 60; margin: 10;")
            butt_frame = CustomFrame(frame, QVBoxLayout, size=(0, 0), bg="lightgreen")
            add_style(butt_frame, "margin: 0;")
            CustomLabel(butt_frame, f"{"Открыта" if categories[name]["status"] else "Закрыта"} для студентов", size=(1, 0))
            butt_frame.setFixedWidth(350)
            add_style(butt_frame, "padding: 10; ")
            Image(butt_frame, f"{name}.png", 330, 330, 300, 300)
            CustomLabel(butt_frame, name, size=(1, 0), font=QFont("Bahnschrift SemiBold", 20))

            if not categories[name]["status"]:
                img_width = 110
                img = Image(frame, "lock.png", img_width, img_width, 90, 90, place=-1)
                img.setStyleSheet("padding: 0;")
                img.setGeometry(int((350 - img_width) / 2), 0, img_width, img_width)

            butt_frame.mousePressEvent = (lambda e, n=name,
                                                 am=categories[name]["amount"] if categories[name]["status"] else None:
                                          open_results_table(n, am))

            status_butt = CustomLabel(frame, f"{"Закрыть" if categories[name]["status"] else "Открыть"} доступ",
                                      size=(1, 0), bg="lightblue")
            add_style(status_butt, "padding: 10;")
            status_butt.mousePressEvent = lambda e, n=name, s=categories[name]["status"]: change_status(n, not s)

            amount_label = CustomLabel(frame,
                                       f"Сейчас пишут: {categories[name]["amount"]}" if categories[name]["status"] else "",
                                       size=(1, 0), font=QFont("Franklin Gothic Heavy", 20))
            add_style(amount_label, "padding: 10;")

# Поле для экспорта Excel-файла
class ExportField:
    def __init__(self, parent, try_export):
        CustomLabel(parent, f"Экспортировать результаты анкетирования в виде Excel-таблицы:",
                    font=QFont("Times New Roman", 25), size=(1, 0))

        row = CustomFrame(parent, QHBoxLayout, size=(1, 0))
        export_frame = CustomFrame(row, QHBoxLayout, size=(0, 0))
        export_frame.layout.setSpacing(30)
        faculty_chose = CustomFrame(export_frame, QtWidgets.QHBoxLayout, size=(0, 0))
        faculty_chose.layout.setSpacing(5)
        faculty_chose.setObjectName("this")
        faculty_chose.setStyleSheet("#this{margin: 30}")

        CustomLabel(faculty_chose, "Факультет:", font=QtGui.QFont("Source Sans Pro", 20))
        fac_combo = QtWidgets.QComboBox(faculty_chose)
        fac_combo.setFont(QtGui.QFont("Source Sans Pro", 20))
        fac_combo.setEditable(True)
        fac_combo.setFixedWidth(250)
        fac_combo.setStyleSheet("padding:5; border-radius:7; border: 4px inset #90ada4; margin-left:20;")
        fac_combo.setIconSize(QSize(40, 40))
        fac_combo.lineEdit().setFont(QtGui.QFont("Source Sans Pro", 20))
        for fac in faculties:
            image_path = os.path.join(os.path.dirname(__file__), 'images/faculty icons', f"{fac.lower()}.png")
            fac_combo.addItem(QIcon(f"{image_path}"), fac)
        fac_combo.setCurrentIndex(-1)
        faculty_chose.layout.addWidget(fac_combo)

        fac_combo.currentTextChanged.connect(
            lambda e: try_export(fac_combo.currentText()))

        self.excel_butt = CustomFrame(export_frame, QtWidgets.QHBoxLayout, size=(0, 0))
        self.excel_butt.layout.setSpacing(10)
        self.excel_butt.setObjectName("this")
        self.excel_butt.setStyleSheet("#this{background-color: #8a8a8a; padding: 10; border-radius: 20;}")
        self.excel_butt.setEnabled(False)

        Image(self.excel_butt, "excel.png", 50, 50)

        text = CustomLabel(self.excel_butt, "Экспорт", size=(0, 0),
                           font=QtGui.QFont("Cascadia Code", 13))
        text.setStyleSheet("color: white;")

        bottom_frame = CustomFrame(parent, QHBoxLayout, size=(1, 0))
        font = QFont("Segoe UI Variable Small Semibol", 20)
        font.setBold(True)
        self.export_info = CustomLabel(bottom_frame, text="", size=(0, 0), font=font)

# Класс таблицы результатов
class ResultsTable:
    def __init__(self, parent, category, amount, get_categories, try_get_answers):
        self.widget = CustomScrollArea(parent, 'v', vert_scroll=True)

        self.widget.elements.setObjectName("back_color")
        self.widget.elements.setStyleSheet("#back_color{background-color: " + window_bg + ";}")

        self.widget.elements.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.widget.layout.setSpacing(30)

        buttons_frame = CustomFrame(self.widget, QHBoxLayout, size=(1, 0))
        back_butt = CustomButton(buttons_frame, "Назад", lambda e: get_categories())
        back_butt.setFixedSize(200, 80)

        CustomLabel(buttons_frame, f"ОЦЕНКА УДОВЛЕТВОРЁННОСТИ {category.upper()}ОВ",
                    font=QFont("Times New Roman", 30), size=(1, 1))

        ExitButton(buttons_frame)

        self.amount_label = CustomLabel(self.widget,
                                        f"Сейчас пишут: {amount}" if amount is not None else "",
                                        size=(1, 0), font=QFont("Franklin Gothic Heavy", 20))
        add_style(self.amount_label, "padding: 10;")

        param_row = CustomFrame(self.widget, QtWidgets.QHBoxLayout, size=(0, 0))
        param_row.layout.setSpacing(5)

        CustomLabel(param_row, "Факультет:", font=QtGui.QFont("Source Sans Pro", 20))
        fac_combo = QtWidgets.QComboBox(param_row)
        fac_combo.setFont(QtGui.QFont("Source Sans Pro", 20))
        fac_combo.setEditable(True)
        fac_combo.setFixedWidth(250)
        fac_combo.setStyleSheet("padding:5; border-radius:7; border: 4px inset #90ada4; margin-left:20;")
        fac_combo.setIconSize(QSize(40, 40))
        fac_combo.lineEdit().setFont(QtGui.QFont("Source Sans Pro", 20))
        for fac in faculties:
            image_path = os.path.join(os.path.dirname(__file__), 'images/faculty icons', f"{fac.lower()}.png")
            fac_combo.addItem(QIcon(f"{image_path}"), fac)
        fac_combo.setCurrentIndex(-1)
        param_row.layout.addWidget(fac_combo)

        if category == "Студент":
            year_chose = CustomFrame(param_row, QtWidgets.QHBoxLayout)
            year_chose.setStyleSheet("margin-left: 50;")
            year_chose.layout.setSpacing(20)
            CustomLabel(year_chose, "Курс:", font=QtGui.QFont("Source Sans Pro", 20))
            year_entry = QtWidgets.QLineEdit(year_chose)
            year_entry.setValidator(QtGui.QIntValidator(parent))
            year_entry.setFont(QtGui.QFont("Source Sans Pro", 20))
            year_entry.setFixedWidth(80)
            year_entry.setAlignment(Qt.AlignCenter)
            year_entry.setStyleSheet("padding:5; border-radius:7; border: 4px inset #90ada4; margin-left:20;")
            year_entry.textChanged.connect(
                lambda e: try_get_answers(category, fac_combo.currentText(), year_entry.text()))
            param_row.layout.addWidget(year_entry)

        fac_combo.currentIndexChanged.connect(
            lambda e: try_get_answers(category, fac_combo.currentText(),
                                           None if category != "Студент" else year_entry.text()))

        # back_butt = CustomButton(param_row, "Внести значения", lambda e, c=category: self.open_insert_window(c))
        # add_style(back_butt, "margin-left: 60;")
        # back_butt.setFixedSize(350, 80)

        self.error_label = CustomLabel(self.widget, size=(1, 0), place=(3,), font=QFont("Franklin Gothic Heavy", 20))
        add_style(self.error_label, "margin: 10; padding: 20;")

        self.temp_frame = CustomFrame(self.widget, QGridLayout, size=(1, 1))

    def open_insert_window(self, category):
        self.child = InsertWindow(category)
        self.child.show()

class InsertWindow(QMainWindow):
    def __init__(self, category):
        super().__init__()

        self.setWindowTitle("Внесение новых данных")

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        main_layout = QGridLayout()
        self.central_widget.layout = main_layout
        self.central_widget.setLayout(main_layout)

        amounts = {"Студент": 8,
                   "Выпускник": 5,
                   "Магистрант": 9}

        self.entries = []

        for row in range(amounts[category]):
            self.entries.append([])
            for col in range(4):
                entry = CustomEntry(self.central_widget, align=Qt.AlignCenter, place=(row, col, 1,1), size=(1,1))
                entry.setText("0")
                self.entries[-1].append(entry)

        CustomButton(self.central_widget, "Внести", lambda e: print(self.entries), place=(amounts[category],1,1,2))

# Класс отображения ответов
class AnswersBlock:
    def __init__(self, parent, rec_data):
        self.table_frame = CustomFrame(parent, QGridLayout, size=(1, 1))

        table = CustomFrame(self.table_frame, QGridLayout, size=(1, 1))
        table.layout.setRowStretch(0, 2)
        table.layout.setRowStretch(1, 20)

        header_table = CustomFrame(table, QGridLayout, place=(0, 1, 1, 1))
        header_table.setObjectName("this")
        header_table.setStyleSheet("#this{padding-right:25}")

        font = QFont("Calibri", 17)
        font.setBold(True)
        header_crit = CustomLabel(table, "Критерии оценки", (0, 0, 1, 1),
                                  font=font, bg="#0be397")
        add_style(header_crit, "border-top-left-radius: 20px")
        header_crit.setFixedWidth(500)

        header_variants = CustomLabel(header_table, "ВАРИАНТЫ ОЦЕНКИ", (0, 0, 1, 4), size=(1, 1),
                                      font=QFont("Calibri", 17), bg="#36d179")
        add_style(header_variants, "padding: 10;")

        header_variants = CustomLabel(header_table, "Процент удовлетворённости", (0, 5, 2, 1), size=(1, 1),
                                      font=QFont("Calibri", 17), bg="#5ce68a")
        add_style(header_variants, "border-top-right-radius: 20px; padding: 10;")
        header_variants.setWordWrap(True)

        chose_headers = ["полностью удовлетворён", "скорее удовлетворён, чем не удовлетворён",
                         "скорее не удовлетворён, чем удовлетворён", "полностью не удовлетворён"]

        font = QFont("Calibri", 17)
        font.setItalic(True)
        col = 0
        for header in chose_headers:
            header_label = CustomLabel(header_table, header, (1, col, 1, 1), size=(1, 1),
                                       font=font, bg="white")
            header_label.setWordWrap(True)
            add_style(header_label, "border: 2 solid black;")
            col += 1

        area = CustomScrollArea(table, 'v', vert_scroll=True, place=(1, 0, 1, 5))
        area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        area.elements.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        area.verticalScrollBar().setStyleSheet("""
                        QScrollBar:vertical {
                            width: 25px;
                        }
                    """)

        answers = rec_data["answers"]
        answers_choose = answers[0]
        answers_text = answers[1]

        for number in range(1, len(answers_choose) + 1):
            row_box = CustomFrame(area, QHBoxLayout)
            question_label = CustomLabel(row_box, f"{number}. {answers_choose[str(number)]['text']}",
                                         align=Qt.AlignLeft,
                                         font=QFont("Calibri", 17), bg="white")
            question_label.setWordWrap(True)
            add_style(question_label, "border: 2px solid black;")
            question_label.setFixedWidth(500)

            for answer_number, amount in answers_choose[str(number)]['answers'].items():
                answer_label = CustomLabel(row_box, str(amount), font=QFont("Arial Rounded MT Bold", 15), size=(1, 1))
                add_style(answer_label, "border: 2 solid black;")

            percent_label = CustomLabel(row_box, f"{round(answers_choose[str(number)]['persent'], 2)}%", size=(1, 1),
                                        font=QFont("Arial Rounded MT Bold", 17))
            add_style(percent_label, "border: 2 solid black;")

        bottom_row = CustomFrame(self.table_frame, QHBoxLayout, size=(1, 0))
        bottom_row.setFixedHeight(100)
        bottom_row.setObjectName("this")
        bottom_row.setStyleSheet("#this{padding-right:25}")
        header_bottom = CustomLabel(bottom_row, f"Среднее:", font=QFont("Calibri", 17), bg="white")
        add_style(header_bottom, "border: 2px solid black; border-bottom-left-radius: 20px")
        header_bottom.setFixedWidth(500)

        for average in rec_data["averages"]:
            average_label = CustomLabel(bottom_row, f"{round(average, 3)}", size=(1, 1),
                                        font=QFont("Arial Rounded MT Bold", 17), bg="white")
            add_style(average_label, "border: 2 solid black;")

        ultimate_label = CustomLabel(bottom_row, f"{round(rec_data['ultimate_satisfaction'], 2)}%",
                                     size=(1, 1), font=QFont("Arial Rounded MT Bold", 19),
                                     bg=get_color_from_percent(rec_data['ultimate_satisfaction']))
        add_style(ultimate_label, "border: 2 solid black; border-bottom-right-radius: 20px")

        for number in range(2, len(answers_text) + 2):
            row_box = CustomFrame(self.table_frame, QVBoxLayout, size=(1, 0))
            text = CustomLabel(row_box, f"{number}. {answers_text[str(number)]['text']}", align=Qt.AlignLeft,
                               size=(1, 0),
                               font=QFont("Times New Roman", 20))
            text.setWordWrap(True)
            add_style(text, "margin: 10; padding: 10")

            area_frame = CustomFrame(row_box, QHBoxLayout, size=(1, 0))

            label = CustomLabel(area_frame, "Ответы: ", font=QFont("Times New Roman", 20))
            label.setStyleSheet("margin: 20;")

            answers_area = CustomScrollArea(area_frame, 'h', vert_scroll=True, horiz_scroll=True)
            answers_area.elements.setObjectName("back_color")
            answers_area.elements.setStyleSheet("#back_color{background-color: " + window_bg + ";}")
            answers_area.layout.setSpacing(10)

            for text in answers_text[str(number)]['answers']:
                text_label = CustomLabel(answers_area, text, size=(1, 1), align=Qt.AlignLeft, bg="white",
                                         font=QFont("Calibri", 17))
                add_style(text_label, "padding:5; border-radius:7; border: 2px solid black;")
                text_label.setFixedWidth(500)
                text_label.setWordWrap(True)