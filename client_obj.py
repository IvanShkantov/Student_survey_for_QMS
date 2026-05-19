import asyncio
import json

from abc import ABC, abstractmethod

from custom_widgets import Message

# Класс наследующий Admin и Client
class ClientObj(ABC):
    def __init__(self, sock, event_loop, widget, init_geometry, back_func, window):
        self.sock = sock
        self.loop = event_loop
        self.task = None

        self.window = widget
        self.init_geometry = init_geometry
        self.widget = None
        self.error_label = None

        self.full_screen = window.showMaximized
        self.app = window
        self.exit = window.close

        self.back_func = back_func

    def set_geometry(self, x,y,w,h):
        self.app.showNormal()
        self.app.setGeometry(x,y,w,h)

    def set_size(self, w, h):
        self.app.showNormal()
        self.app.resize(w,h)

    # Получение доступных категорий
    async def available_categories(self):
        try:
            send_data = json.dumps({"action": "categories"})
            await self.loop.sock_sendall(self.sock, send_data.encode('utf-8'))

            rec_data = await self.loop.sock_recv(self.sock, 1024)

            print(rec_data)

            categories = json.loads(rec_data.decode('utf-8'))["categories"]

            self.show_categories(categories)

        except Exception as e:
            Message("ERROR", f"Ошибка получения доступных категорий: {e}", 'c')

    # Отслеживание изменений
    @abstractmethod
    def get_changes(self):
        pass

    # Отображение категорий
    @abstractmethod
    def show_categories(self, categories):
        pass

    # Возвращение на окно выбора роли
    @abstractmethod
    def go_back(self):
        pass

    # Запуск цикла получения данных
    def start_receiving_cycle(self):
        self.set_geometry(self.init_geometry[0], self.init_geometry[1],
                          self.init_geometry[2], self.init_geometry[3])
        asyncio.create_task(self.available_categories())
        self.task = asyncio.create_task(self.get_changes())