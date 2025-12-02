from app.body.interfaces import IMessageBus
from app.body.messaging.in_memory_bus import InMemoryMessageBus


class BodyServiceProvider:
    """
    Фабрика или контейнер для предоставления общих зависимостей Тела.
    """

    def __init__(self, logger_instance):
        # 1. Основные органы Тела (глобальные, если нет абстракций)
        self.logger = logger_instance
        # 2. Абстракции Тела (IMessageBus)
        self.message_bus: IMessageBus = InMemoryMessageBus()
        # self.config_reader = config_reader_instance  # Пример IConfigReader

    def get_common_dependencies(self) -> dict:
        """
        Возвращает словарь всех общих зависимостей, готовых к инъекции.
        """
        return {
            "message_bus": self.message_bus,
            "logger": self.logger,
            # "config_reader": self.config_reader, # Если нужно
        }

    def get_message_bus(self) -> IMessageBus:
        return self.message_bus
