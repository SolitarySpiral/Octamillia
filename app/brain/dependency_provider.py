from typing import Dict

from app.body.interfaces import IMessageBus
from app.body.messaging.hearth import HeartBus


class BodyServiceProvider:
    def __init__(self, logger_instance, bus_implementations: Dict[str, IMessageBus]):
        self.logger = logger_instance

        # 1. Храним реализации, которые нам передали
        self.bus_implementations = bus_implementations

        # 2. Создаем Сердце из того, что получили
        self.heart = HeartBus(buses=self.bus_implementations)

        print("[PROVIDER] Провайдер инициализирован. Шины загружены извне.")

    def get_common_dependencies(self) -> dict:
        return {
            "message_bus": self.heart,  # <-- Щупальца получают Сердце
            "logger": self.logger,
        }

    # Для тестов, если нужно достучаться до конкретной вены
    def get_heart(self) -> HeartBus:
        return self.heart
