import asyncio
import json

from custom_widgets import CustomFrame, Message, CustomButton, ExitButton, CustomLabel, Image
from gui import QuestionnaireForm
from static_functions import add_style, clear_layout
from database import faculties
from config import MAX_SIZE

from client_obj import ClientObj

from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout

from PyQt5.QtGui import QFont

# Класс роли Студент
class Student(ClientObj):
    def __init__(self, sock, event_loop, widget, init_geometry, back_func, app):
        super().__init__(sock, event_loop, widget, init_geometry, back_func, app)
        self.start_receiving_cycle()

    # Возвращение на окно выбора роли
    def go_back(self):
        clear_layout(self.window.layout)
        if self.task is not None:
            self.task.cancel()
        self.back_func()

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
                    self.show_categories(data["categories"])
                elif data["action"] == "questionnaire": # Получение анкеты
                    self.open_questionnaire(data["category"], data["questions"])
                    break

        except Exception as e:
            Message("ERROR", f"Ошибка получения в цикле ожидания: {e}", 'c')

    # Отображение категорий
    def show_categories(self, categories):
        if self.widget is not None:
            self.widget.deleteLater()

        self.widget = CustomFrame(self.window, QVBoxLayout)

        buttons_frame = CustomFrame(self.widget, QHBoxLayout, size=(1,0))

        back_butt = CustomButton(buttons_frame, "Назад", lambda: self.go_back())
        back_butt.setFixedSize(200,80)

        CustomFrame(buttons_frame, QHBoxLayout, size=(1,1))
        ExitButton(buttons_frame)

        label = CustomLabel(self.widget, f"Для начала анкетирования выберите необходимую категорию из доступных:",
                    font=QFont("Times New Roman", 25), size=(1,0))

        label.setWordWrap(True)
        label.setStyleSheet("margin: 30,0,0,0;")

        buttons = CustomFrame(self.widget, QHBoxLayout)

        buttons.layout.setSpacing(0)

        for name in categories.keys():
            butt_frame = CustomFrame(buttons, QVBoxLayout, size=(0, 0), bg="lightgreen")
            butt_frame.setFixedWidth(200)
            add_style(butt_frame, "padding: 10;")
            Image(butt_frame, f"{name}.png", 180, 180, 150, 150)
            CustomLabel(butt_frame, name, size=(1, 0), font=QFont("Bahnschrift SemiBold", 15))

            if not categories[name]["status"]:
                img = Image(butt_frame, "lock.png", 100, 100, place=-1)
                img.setStyleSheet("padding: 0;")
                img.setGeometry(50, 90, 100, 100)
            else:
                butt_frame.mousePressEvent = lambda e, n=name: self.get_questions(n)

    # Отправка анкеты
    def send_form(self, category, buttons_groups, text_answers, faculty, course, date_now):
        data = {"answers": [{}, {}],
                "info": {"category": category}}

        try:
            if faculty.strip() == "":
                raise RuntimeError("Не указан факультет")
            elif faculty not in faculties:
                raise RuntimeError("Некорректное название факультета")

            data["info"]["faculty"] = faculty

            if course is None:
                data["info"]["course"] = None
            elif course.strip() == "":
                raise RuntimeError("Не указан курс")
            elif int(course) <= 0:
                raise RuntimeError("Некорректно указан курс")
            else:
                data["info"]["course"] = int(course)

            data["info"]["date"] = date_now

            for quest_id, buttons in buttons_groups.items():
                if buttons.checkedButton() is None:
                    raise RuntimeError("Не для всех критериев выбрана отметка")

                data["answers"][0][quest_id] = str(buttons.id(buttons.checkedButton()))

            for quest_id, textbox in text_answers.items():
                if textbox.toPlainText().strip() != "":
                    data["answers"][1][quest_id] = textbox.toPlainText()

            async def send_async():
                try:
                    send_data = {"action": "send",
                                 "data": data}

                    marked_data = '#' + json.dumps(send_data) + "<end>"

                    await self.loop.sock_sendall(self.sock, marked_data.encode('utf-8'))

                    rec_data = await self.loop.sock_recv(self.sock, MAX_SIZE)
                    status = json.loads(rec_data.decode('utf-8'))["status"]

                    self.widget.deleteLater()

                    if status == "success":
                        self.widget = CustomFrame(self.window, QVBoxLayout)
                        CustomLabel(self.widget, f"АНКЕТА ОТПРАВЛЕНА\nСпасибо!",
                                    font=QFont("Times New Roman", 40))

                        butt = CustomFrame(self.widget, QHBoxLayout, size=(1, 0))
                        butt.setFixedHeight(200)
                        butt.layout.setSpacing(450)
                        CustomButton(butt, "В меню", lambda: self.start_receiving_cycle(), font=QFont("Bahnschrift", 25))
                        exit_butt = CustomButton(butt, "Выход", lambda: self.exit(), font=QFont("Bahnschrift", 25))
                        exit_butt.setStyleSheet("padding:15; border-radius:30; background-color: #e38d8d; border: 5 inset #ad3d3d;")

                except Exception as e:
                    Message("ERROR", f"Ошибка отправки: {e}",'c')

            asyncio.create_task(send_async())

        except RuntimeError as error:
            add_style(self.error_label, "background-color: red;")
            self.error_label.setText(str(error))

    # Закрытие анкеты
    def close_questionnaire(self, category):
        async def categories():
            try:
                send_data = json.dumps({"action": "form_closed",
                                        "category": category})
                await self.loop.sock_sendall(self.sock, send_data.encode('utf-8'))
            except Exception as e:
                Message("ERROR", f"Ошибка при закрытии анкеты: {e}", 'c')

        asyncio.create_task(categories())
        self.start_receiving_cycle()

    # Открытие анкеты
    def open_questionnaire(self, category, questions):
        self.widget.deleteLater()
        self.full_screen()

        form = QuestionnaireForm(self.window, category, questions,
                                 self.close_questionnaire, self.send_form)

        self.widget = form.widget
        self.error_label = form.error_label

    # Получение вопросов
    def get_questions(self, category):
        async def get_questions_async():
            try:
                send_data = json.dumps({"action": "questions",
                                        "category": category})

                await self.loop.sock_sendall(self.sock, send_data.encode('utf-8'))

            except Exception as e:
                Message("ERROR", f"Ошибка получения вопросов: {e}", 'c')

        asyncio.create_task(get_questions_async())

