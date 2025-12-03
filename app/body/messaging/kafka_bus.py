import asyncio
from typing import Callable

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer

from app.body.blood import OctaEvent  # Ваша модель события

from ..interfaces import IMessageBus


class KafkaMessageBus(IMessageBus):
    def __init__(
        self, bootstrap_servers: str = "localhost:9092", group_id: str = "octamillia_main_group"
    ):
        self.bootstrap_servers = bootstrap_servers
        self.group_id = group_id
        self.producer = None
        # Храним активные таски consumer-ов, чтобы они не собирались GC
        self.active_tasks = []

    async def start(self):
        """Инициализация продюсера (нужно вызвать при старте Тела)"""
        self.producer = AIOKafkaProducer(bootstrap_servers=self.bootstrap_servers)
        await self.producer.start()
        print(f"[KAFKA BUS] ✅ Продюсер подключен к {self.bootstrap_servers}")

    async def stop(self):
        """Гарантирует корректное завершение работы продюсера и консьюмеров."""
        # 1. Сначала останавливаем Producer
        if self.producer:
            await self.producer.stop()
            print("[KAFKA BUS] 🔴 Продюсер остановлен.")

        # 2. Аккуратно отменяем все запущенные Consumer-таски
        if self.active_tasks:
            print(f"[KAFKA BUS] 🛑 Отменяю {len(self.active_tasks)} фоновых задач...")
            for task in self.active_tasks:
                if not task.done():
                    # Посылаем сигнал отмены
                    task.cancel()

            # Ждем завершения всех отмененных тасков с таймаутом
            await asyncio.gather(*self.active_tasks, return_exceptions=True)
            print("[KAFKA BUS] ✅ Все Consumer-задачи отменены.")

        # Очищаем список после завершения
        self.active_tasks.clear()

    async def publish(self, topic: str, message: OctaEvent):
        """
        Сериализуем OctaEvent в JSON и отправляем в байтах.
        """
        if not self.producer:
            await self.start()  # Ленивый старт, если забыли вызвать явно

        # Pydantic v2: model_dump_json() -> превращаем объект в строку
        value_json = message.model_dump_json()

        try:
            await self.producer.send_and_wait(topic, value=value_json.encode("utf-8"))
            print(f"[KAFKA BUS] 📤 Отправлено в '{topic}': {message.event}")
        except Exception as e:
            print(f"[KAFKA BUS] ❌ Ошибка отправки: {e}")

    async def subscribe(self, topic: str, handler: Callable):
        """
        Создает отдельную задачу (Consumer) для прослушивания топика.
        """
        print(f"[KAFKA BUS] 🎧 Подписка на '{topic}' (Handler: {handler.__name__})")

        # Запускаем бесконечный цикл чтения в фоне
        task = asyncio.create_task(self._consumption_loop(topic, handler))
        self.active_tasks.append(task)

    async def _consumption_loop(self, topic: str, handler: Callable):
        """
        Внутренний цикл, который висит на Kafka и ждет сообщений.
        """
        consumer = AIOKafkaConsumer(
            topic,
            bootstrap_servers=self.bootstrap_servers,
            group_id=self.group_id,
            # Начинаем читать с ранних сообщений, если группа новая
            auto_offset_reset="earliest",
        )

        await consumer.start()
        try:
            async for msg in consumer:
                try:
                    # 1. Десериализация: Байты -> JSON -> OctaEvent
                    payload_str = msg.value.decode("utf-8")
                    event_data = OctaEvent.model_validate_json(payload_str)

                    print(f"[KAFKA BUS] 📥 Получено из '{topic}': {event_data.event}")

                    # 2. Вызов обработчика Щупальца
                    await handler(event_data)

                except Exception as e:
                    print(f"[KAFKA BUS] ⚠️ Ошибка обработки сообщения: {e}")
        finally:
            await consumer.stop()
