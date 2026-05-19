import asyncio
import json
import socket
import atexit

from config import admin_key, PORT, CLIENTS_AMOUNT, MAX_SIZE
from database import DataBase

# Класс Сервер
class Server:
    # Инициализация начальных значений
    def __init__(self, port=PORT):
        self.admin_key = admin_key
        self.host = ""
        self.port = port
        self.loop = None
        self.clients = []
        self.admins = []
        self.sock_category = {}
        self.categories = {"Студент": {},
                           "Выпускник": {},
                           "Магистрант": {}}

        for category in self.categories.keys():
            self.categories[category] = {"status": False, "amount": 0}

        # Подключение базы данных
        self.database = DataBase()

        # Инициализация сокета
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.setblocking(False)

    # Функция для запуска сервера
    async def start_server(self):
        self.host = input("Введите локальный адрес сервера: ")

        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(CLIENTS_AMOUNT)

        print(f'Сервер запущен на {self.host}:{self.port}')
        await self.accept_connections()

    # Ожидание подключения клиентов
    async def accept_connections(self):
        self.loop = asyncio.get_event_loop()
        while True:
            # Инициализация клиентского сокета
            client_socket, addr = await self.loop.sock_accept(self.server_socket)
            client_socket.setblocking(False)
            asyncio.create_task(self.handle_client(client_socket, addr))

    # Обработка подключившегося клиента
    async def handle_client(self, client_socket, addr):
        print(f"Новое подключение от {addr}")

        self.clients.append(client_socket)

        # Бесконечный цикл обработки полученных данных
        try:
            while True:
                decoded = ""
                while True:
                    rec_data = await self.loop.sock_recv(client_socket, MAX_SIZE)
                    if not rec_data:
                        break

                    decoded += rec_data.decode('utf-8')

                    if decoded[0] == '#':
                        if "<end>" in decoded:
                            decoded = decoded[1:-5]
                            break
                    else:
                        break

                if decoded == "":
                    break

                data = json.loads(decoded)

                print("Получено <--- ", data)

                action = data["action"]

                send_data = ""
                broadcast = False # Флаг отправки всем клиентам
                long = False # Флаг длинного сообщения

                if action == "enter": # Проверка входа в учётную запись
                    send_data = self.database.check_enter_data(data["login"], data["password"])
                    if send_data["access"]:
                        self.admins.append(client_socket)

                elif action == "registrate": # Проверка данных регистрации
                    if data["admin_key"] != self.admin_key:
                        send_data = {"access": False, "error": "Неверный ключ доступа"}
                    else:
                        send_data = self.database.new_admin(data["login"], data["password"])
                        if send_data["access"]:
                            self.admins.append(client_socket)

                elif action == "log_out": # Выход из учётной записи
                    self.admins.remove(client_socket)
                    continue

                elif action == "form_closed": # Закрытие анкеты
                    self.categories[data["category"]]["amount"] -= 1
                    self.sock_category.pop(client_socket)
                    await self.notify_admins({"action": "update_categories",
                                              "categories": self.categories})
                    continue

                elif action == "categories": # Получение категорий
                    send_data = {"action": "update_categories",
                                 "categories": self.categories}

                elif action == "status": # Изменение статуса категории
                    broadcast = True
                    self.categories[data["category"]]["status"] = data["status"]
                    send_data = {"action": "update_categories",
                                 "categories": self.categories}

                elif action == "questions": # Получение списка вопросов
                    long = True
                    cat = data["category"]
                    self.categories[cat]["amount"] += 1
                    self.sock_category[client_socket] = cat
                    questions = self.database.get_questions(cat)
                    send_data = {"action": "questionnaire",
                                 "category": cat,
                                 "questions": questions}
                    await self.notify_admins({"action": "update_categories",
                                              "categories": self.categories})

                elif action == "send": # Отправка анкеты
                    self.database.write_answers(data["data"])
                    send_data = {"action": "update_answers",
                                 "status": "success"}
                    self.categories[data["data"]["info"]["category"]]["amount"] -= 1
                    self.sock_category.pop(client_socket)
                    await self.notify_admins({"action": "update_categories",
                                              "categories": self.categories})
                    await self.notify_admins(send_data)

                elif action == "answers": # Получение ответов
                    long = True
                    answers = self.database.get_answers(data["data"])
                    send_data = {"action": "table",
                                 "answers": answers}

                elif action == "get_stats": # Получение отчёта Excel
                    long = True
                    is_exist = self.database.get_faculty_stat(data["faculty"])
                    send_data = {"action": "excel_file",
                                 "file": None}

                    if is_exist is not None:
                        send_data = {"action": "excel_file",
                                     "file": is_exist[0],
                                     "faculty": data["faculty"],
                                     "percent": is_exist[1]}

                print("Отправляю ---> ", send_data)

                clients = list(self.clients)

                if broadcast:
                    for writer in self.sock_category.keys(): # Исключение пользователей, заполняющих анкету
                        clients.remove(writer)

                for sock in clients if broadcast else (client_socket,):
                    if long:
                        data = '#' + json.dumps(send_data) + "<end>"
                    else:
                        data = json.dumps(send_data)
                    # Отправка ответа клиенту
                    await self.loop.sock_sendall(sock, data.encode('utf-8'))

        except Exception as e:
            print(f"Ошибка при обработке клиента: {e}")

        finally:
            # Закрытие соединения
            self.clients.remove(client_socket)
            if client_socket in self.admins:
                self.admins.remove(client_socket)
            elif client_socket in self.sock_category.keys():
                self.categories[self.sock_category[client_socket]]["amount"] -= 1
                self.sock_category.pop(client_socket)
                await self.notify_admins({"action": "update_categories",
                                          "categories": self.categories})
            client_socket.close()
            print(f"Клиент {addr} отключился")

    # Рассылка всем администраторам
    async def notify_admins(self, data):
        print("Рассылаю админам: ", data)
        for sock in self.admins:
            await self.loop.sock_sendall(sock, json.dumps(data).encode('utf-8'))

# Запуск программы
if __name__ == "__main__":
    server = Server()

    def end():
        server.server_socket.close()

    atexit.register(end)

    try:
        asyncio.run(server.start_server())
    except KeyboardInterrupt:
        print("Сервер остановлен")
        server.server_socket.close()
