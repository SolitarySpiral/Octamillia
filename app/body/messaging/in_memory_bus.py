import asyncio
from typing import Callable, Dict

from app.body.blood import OctaEvent  # Ваш унифицированный тип
from app.body.interfaces import IMessageBus


class InMemoryMessageBus(IMessageBus):
    def __init__(self):
        # Queues: Топик (str) -> Очередь (asyncio.Queue)
        self.queues: Dict[str, asyncio.Queue] = {}
        # Handlers: Топик (str) -> Функция-обработчик (Callable)
        self.handlers: Dict[str, Callable] = {}

    async def publish(self, topic: str, message: OctaEvent):
        """Отправитель просто кладет сообщение в очередь."""
        if topic not in self.queues:
            # Создаем очередь, если ее нет (автоматическое создание топика)
            self.queues[topic] = asyncio.Queue()

        print(f"[BUS] 📤 Сообщение '{message.event}' отправлено в топик '{topic}'.")
        await self.queues[topic].put(message)

    async def subscribe(self, topic: str, handler: Callable):
        """Регистрирует обработчик и запускает постоянную задачу прослушивания."""
        if topic in self.handlers:
            # Убедимся, что на один топик подписывается только один обработчик
            print(f"[BUS] ⚠️ Топик '{topic}' уже имеет обработчик. Игнорируем.")
            return

        if topic not in self.queues:
            self.queues[topic] = asyncio.Queue()

        self.handlers[topic] = handler

        print(f"[BUS] ✅ Подписка на топик '{topic}' установлена. Запускаем слушателя...")

        # Запускаем непрерывную задачу, которая будет "потреблять" сообщения.
        asyncio.create_task(self._listener_task(topic))

    async def _listener_task(self, topic: str):
        """
        Непрерывная задача прослушивания (Listener), которая достает сообщения
        из очереди и вызывает обработчик Щупальца.
        """
        queue = self.queues[topic]
        handler = self.handlers[topic]

        while True:
            # Блокировка: ждем, пока в очереди появится сообщение
            message: OctaEvent = await queue.get()

            print(f"[BUS] 📥 Сообщение '{message.event}' получено из '{topic}'.")

            # === СУТЬ ЛОГИКИ ОБРАБОТКИ ===
            # Вызываем функцию-обработчик (метод Щупальца)
            try:
                # Предполагаем, что обработчик - это асинхронная функция
                await handler(message)
            except Exception as e:
                print(f"[BUS] ❌ Ошибка обработки сообщения в {topic}: {e}")

            # Уведомляем очередь, что элемент обработан
            queue.task_done()


# 1. Сборка Мозга (инициализация долговременных инстансов)
bus = InMemoryMessageBus()
