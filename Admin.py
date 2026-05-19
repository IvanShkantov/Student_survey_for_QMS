import asyncio
import json


from client_obj import ClientObj

from custom_widgets import *
from database import faculties
from config import MAX_SIZE
from gui import AdminCategories, ExportField, ResultsTable, AnswersBlock
from static_functions import clear_layout, add_style, get_color_from_percent

from PyQt5.QtWidgets import QHBoxLayout, QLineEdit, QVBoxLayout

from PyQt5.QtGui import QFont

# Класс роли Администратор
class Admin(ClientObj):
    def __init__(self, sock, event_loop, widget, init_geometry, back_func, app):
        super().__init__(sock, event_loop, widget, init_geometry, back_func, app)

        self.table_frame = None
        self.looking_table = None

        self.entered = False
        self.opened_category = None

        self.excel_butt = None
        self.export_info = None

        self.amount_label = None
        self.temp_frame = None

        self.entry_window()

    # Возвращение на окно выбора роли
    def go_back(self):
        clear_layout(self.window.layout)
        if self.entered:
            asyncio.create_task(self.log_out())

        if self.task is not None:
            self.task.cancel()
        self.back_func()

    # Выход из учётной записи
    async def log_out(self):
        data = {"action": "log_out"}

        send_data = json.dumps(data)
        await self.loop.sock_sendall(self.sock, send_data.encode('utf-8'))

    # Бесконечный цикл обработки данных поступающих от сервера
    async def get_changes(self):
        try:
            while True:
                decoded = ""
                while True:
                    rec_data = await self.loop.sock_recv(self.sock, MAX_SIZE)
                    if not rec_data:
                        break

                    decoded += rec_data.decode('utf-8')
                    if decoded[0] == '#':
                        if "<end>" in decoded:
                            decoded = decoded[1:-5]
                            break
                    else:
                        break

                data = json.loads(decoded)

                if data["action"] == "update_categories": # Обновление параметров категорий
                    if self.opened_category is None:
                        self.show_categories(data["categories"])
                    else:
                        self.update_curr_amount(data["categories"][self.opened_category])
                elif data["action"] == "table":     # Получение таблицы ответов
                    self.show_answers(data["answers"])
                elif data["action"] == "update_answers" and self.looking_table is not None:  # Обновление ответов
                    self.get_answers(self.looking_table)
                elif data["action"] == "excel_file":  # Получение битов Excel-фвйла
                    self.enable_export(data)

        except Exception as e:
            print(f"Ошибка при получении сообщения: {e}")

    # Обновление количества
    def update_curr_amount(self, category_dict):
        self.amount_label.setText(f"Сейчас пишут: {category_dict["amount"]}" if category_dict["status"] else "")

    # Проверка полученного файла Excel на возможность сохранения
    def enable_export(self, data):
        if data["file"] is None:
            self.export_info.setText("Результаты не найдены")
            self.export_info.setStyleSheet("padding: 20; margin: 10; border-radius: 20px; background-color: #ff7373;")
            self.excel_butt.setEnabled(False)
        else:
            self.export_info.setText(f"Процент удовлетворённости: {round(data["percent"], 2)}%")
            self.export_info.setStyleSheet(f"padding: 20; margin: 10; border-radius: 20px; background-color: {get_color_from_percent(data["percent"])};")
            self.excel_butt.setEnabled(True)
            self.excel_butt.setStyleSheet("#this{background-color: #217346; padding: 10; border-radius: 20;}")
            self.excel_butt.mousePressEvent = lambda e: save_excel(data["file"], data["faculty"])

    # Отображение категорий
    def show_categories(self, categories):
        if self.widget is not None:
            self.widget.deleteLater()

        self.widget = AdminCategories(self.window, categories,
                                      self.go_back, self.open_results_table, self.change_status).widget

        export_field = ExportField(self.widget, self.try_export)
        self.excel_butt = export_field.excel_butt
        self.export_info = export_field.export_info


    def open_results_table(self, category, amount):
        self.widget.deleteLater()
        self.full_screen()
        self.table_frame = None
        self.opened_category = category

        table = ResultsTable(self.window, category, amount,
                             self.get_categories, self.try_get_answers)

        self.widget = table.widget
        self.amount_label = table.amount_label
        self.error_label = table.error_label
        self.temp_frame = table.temp_frame

    # Попытка получить файл
    def try_export(self, faculty):
        self.excel_butt.setStyleSheet("#this{background-color: #8a8a8a; padding: 10; border-radius: 20;}")
        self.excel_butt.setEnabled(False)
        self.export_info.setText("")
        self.export_info.setStyleSheet("")

        if faculty.strip() == "":
            return
        elif faculty not in faculties:
            return

        asyncio.create_task(self.get_file(faculty))

    # Запрос на получение файла
    async def get_file(self, faculty):
        try:
            data = {"action": "get_stats",
                    "faculty": faculty}

            send_data = json.dumps(data)
            await self.loop.sock_sendall(self.sock, send_data.encode('utf-8'))

        except Exception as e:
            Message("ERROR", f"Ошибка получения: {e}", 'c')

    def get_answers(self, form_params):
        self.looking_table = form_params
        async def get_answers_async():
            try:
                send_data = json.dumps({"action": "answers",
                                        "data": form_params})

                await self.loop.sock_sendall(self.sock, send_data.encode('utf-8'))

            except Exception as e:
                Message("ERROR", f"Ошибка получения: {e}", 'c')

        asyncio.create_task(get_answers_async())

    def change_status(self, category, status):
        async def change_status_async():
            try:
                send_data = json.dumps({"action": "status",
                                        "category": category,
                                        "status": status})

                await self.loop.sock_sendall(self.sock, send_data.encode('utf-8'))

            except Exception as e:
                Message("ERROR", f"Ошибка получения: {e}", 'c')

        asyncio.create_task(change_status_async())

    # Окно входа в учётную запись
    def entry_window(self):
        if self.widget is not None:
            self.widget.deleteLater()

        self.set_size(853, 592)

        self.widget = CustomFrame(self.window, QVBoxLayout)

        buttons_frame = CustomFrame(self.widget, QHBoxLayout, size=(1, 0))
        back_butt = CustomButton(buttons_frame, "Назад", lambda: self.go_back())
        back_butt.setFixedSize(200, 80)
        CustomFrame(buttons_frame, QHBoxLayout, size=(1, 1))
        ExitButton(buttons_frame)

        font = QFont("Calibri", 45)
        font.setBold(True)
        title = CustomLabel(self.widget, "Вход", font=font, size=(1,1))
        self.widget.layout.addWidget(title)

        login_entry = CustomEntry(self.widget, "Логин")
        password_entry = CustomEntry(self.widget, "Пароль")
        password_entry.setEchoMode(QLineEdit.Password)

        CustomButton(self.widget, "Войти", lambda : self.login(login_entry.text(), password_entry.text()))

        text_frame = CustomFrame(self.widget, QHBoxLayout, size=(1,1))

        CustomLabel(text_frame, "Нет учётной записи?", size=(0,1))
        reg_butt = CustomLabel(text_frame, "Зарегистрируйтесь", size=(0,1), color="blue")
        reg_butt.mousePressEvent = lambda e: self.reg_window()

        self.error_label = CustomLabel(self.widget, size=(1,1))

    # Окно регистрации
    def reg_window(self):
        self.widget.deleteLater()

        self.widget = CustomFrame(self.window, QVBoxLayout)

        buttons_frame = CustomFrame(self.widget, QHBoxLayout, size=(1, 0))
        back_butt = CustomButton(buttons_frame, "Назад", lambda: self.go_back())
        back_butt.setFixedSize(200, 80)
        CustomFrame(buttons_frame, QHBoxLayout, size=(1, 1))
        ExitButton(buttons_frame)

        font = QFont("Calibri", 45)
        font.setBold(True)
        title = CustomLabel(self.widget, "Регистрация", font=font, size=(1, 0))
        self.widget.layout.addWidget(title)

        key_entry = CustomEntry(self.widget, "Ключ доступа")
        key_entry.setEchoMode(QLineEdit.Password)
        login_entry = CustomEntry(self.widget, "Логин")
        password_entry = CustomEntry(self.widget, "Пароль")
        password_entry.setEchoMode(QLineEdit.Password)
        pass_dub_entry = CustomEntry(self.widget, "Повторите пароль")
        pass_dub_entry.setEchoMode(QLineEdit.Password)

        CustomButton(self.widget, "Зарегистрироваться", lambda: self.registration(
            key_entry.text(),
            login_entry.text(),
            password_entry.text(),
            pass_dub_entry.text()))

        text_frame = CustomFrame(self.widget, QHBoxLayout, size=(1, 1))

        CustomLabel(text_frame, "Есть учётная запись?", size=(0, 0))
        reg_butt = CustomLabel(text_frame, "Войдите", size=(0, 0), color="blue")
        reg_butt.mousePressEvent = lambda e: self.entry_window()

        self.error_label = CustomLabel(self.widget)


    # Регистрация, с последующим запросом на сервер
    def registration(self, key, login, password, dub_pass):
        if (key.strip() == "" or
            login.strip() == "" or
            password.strip() == ""):
            self.error_label.setStyleSheet("background-color: red;")
            self.error_label.setText("Поля не заполнены")
        elif password != dub_pass:
            self.error_label.setStyleSheet("background-color: red;")
            self.error_label.setText("Пароли не совпадают")
        else:
            async def registrate():
                try:
                    enter_data = {"action": "registrate",
                                  "admin_key": key,
                                  "login": login,
                                  "password": password}

                    send_data = json.dumps(enter_data)
                    await self.loop.sock_sendall(self.sock, send_data.encode('utf-8'))

                    rec_data = await self.loop.sock_recv(self.sock, MAX_SIZE)
                    rec_dict = json.loads(rec_data.decode('utf-8'))

                    if rec_dict["access"]:
                        self.entered = True
                        self.start_receiving_cycle()
                    else:
                        self.error_label.setStyleSheet("background-color: red;")
                        self.error_label.setText(rec_dict["error"])

                except Exception as e:
                    Message("ERROR", f"Ошибка получения: {e}", 'c')

            asyncio.create_task(registrate())

    # Авторизация, с последующим запросом на сервер
    def login(self, login, password):
        if login.strip() == "" or password.strip() == "":
            self.error_label.setStyleSheet("background-color: red;")
            self.error_label.setText("Поля не заполнены")
        else:
            async def log_in():
                try:
                    enter_data = {"action": "enter",
                                  "login": login,
                                  "password": password}

                    send_data = json.dumps(enter_data)
                    await self.loop.sock_sendall(self.sock, send_data.encode('utf-8'))

                    rec_data = await self.loop.sock_recv(self.sock, MAX_SIZE)
                    rec_dict = json.loads(rec_data.decode('utf-8'))

                    if rec_dict["access"]:
                        self.entered = True
                        self.start_receiving_cycle()
                    else:
                        self.error_label.setStyleSheet("background-color: red;")
                        self.error_label.setText(rec_dict["error"])

                except Exception as e:
                    Message("ERROR", f"Ошибка получения: {e}", 'c')

            asyncio.create_task(log_in())

    # Запрос на получение категорий
    def get_categories(self):
        self.opened_category = None
        self.set_geometry(self.init_geometry[0], self.init_geometry[1],
                          self.init_geometry[2], self.init_geometry[3])
        async def categories():
            try:
                send_data = json.dumps({"action": "categories"})
                await self.loop.sock_sendall(self.sock, send_data.encode('utf-8'))
            except Exception as e:
                Message("ERROR", f"Ошибка получения: {e}", 'c')

        asyncio.create_task(categories())

    # Отображение ответов
    def show_answers(self, rec_data):
        if rec_data is None:
            add_style(self.error_label, "background-color: red;")
            self.error_label.setText("Ответы не найдены")
        else:
            if self.error_label is not None:
                self.error_label.deleteLater()
                self.error_label = None
            if self.table_frame is not None:
                self.table_frame.deleteLater()

            self.table_frame = AnswersBlock(self.temp_frame, rec_data).table_frame

    # Попытка получения ответов при изменении параметров
    def try_get_answers(self, category, faculty, course):
        if self.table_frame is not None:
            self.table_frame.deleteLater()
            self.error_label = CustomLabel(self.widget, size=(1, 0), font=QFont("Franklin Gothic Heavy", 20), place=(3,))
            add_style(self.error_label, "margin: 10; padding: 20; background-color: red;")

            self.table_frame = None
        try:
            if faculty.strip() == "":
                raise RuntimeError("Не указан факультет")
            elif faculty not in faculties:
                raise RuntimeError("Некорректное название факультета")

            if course is None:
                course = 0
            elif course.strip() == "":
                raise RuntimeError("Не указан курс")
            elif int(course) <= 0:
                raise RuntimeError("Некорректно указан курс")


            self.get_answers({'category': category,
                              'faculty': faculty,
                              'course': course})

        except RuntimeError as error:
            add_style(self.error_label, "background-color: red;")
            self.error_label.setText(str(error))

