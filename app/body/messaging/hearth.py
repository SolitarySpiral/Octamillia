import asyncio
from typing import Callable, Dict

from app.body.blood import OctaEvent
from app.body.interfaces import IMessageBus


class HeartBus(IMessageBus):
    """
    Агрегатор всех шин данных.
    Работает как мультиплексор: отправляет во все, слушает из всех.
    """

    def __init__(self, buses: Dict[str, IMessageBus]):
        self.buses = buses  # {'kafka': KafkaBus(...), 'inmemory': InMemoryBus(...)}

    async def start(self):
        """Запускает все подключенные шины (если им это нужно)."""
        for name, bus in self.buses.items():
            if hasattr(bus, "start"):
                try:
                    await bus.start()
                    print(f"[HEART] ✅ Шина '{name}' запущена.")
                except Exception as e:
                    print(f"[HEART] ⚠️ Ошибка запуска шины '{name}': {e}")

    async def stop(self):
        """Останавливает все шины."""
        for name, bus in self.buses.items():
            if hasattr(bus, "stop"):
                await bus.stop()

    async def publish(self, topic: str, message: OctaEvent, target_bus: str = None):
        """
        Отправляет сообщение.
        Если target_bus не указан -> отправляет во ВСЕ живые шины (Broadcast).
        Если указан -> только в конкретную.
        """
        if target_bus:
            # Точечная отправка (например, только в тесте)
            if target_bus in self.buses:
                await self.buses[target_bus].publish(topic, message)
            else:
                print(f"[HEART] ❌ Шина '{target_bus}' не найдена.")
            return

        # Broadcast: качаем кровь везде
        tasks = []
        for name, bus in self.buses.items():
            # Можно добавить проверку healthcheck, жива ли шина
            tasks.append(bus.publish(topic, message))

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def subscribe(self, topic: str, handler: Callable):
        """
        Подписывает обработчик Щупальца на этот топик во ВСЕХ шинах.
        Где бы ни появилось сообщение (Kafka или Memory), Щупальце его получит.
        """
        for name, bus in self.buses.items():
            # 👇 СОЗДАНИЕ КОНТЕКСТНОЙ ОБЕРТКИ
            # Эта функция будет вызвана underlying bus (KafkaBus или InMemoryBus)
            async def contextual_handler(event: OctaEvent, bus_name_for_closure=name):
                # Вызываем оригинальный обработчик, передавая зафиксированное имя
                await handler(event, source_bus=bus_name_for_closure)

            try:
                # Оригинальный bus подписывает обертку (contextual_handler),
                # которая ожидает только один аргумент (event) от своего брокера.
                await bus.subscribe(topic, contextual_handler)
                print(f"[HEART] 🔗 Привязал подписку '{topic}' к шине '{name}'")
            except Exception as e:
                print(f"[HEART] ⚠️ Не удалось подписаться на '{name}': {e}")
