# app/body/interfaces.py
from abc import ABC, abstractmethod
from typing import Callable

from .blood import OctaEvent


# (IMessageBus - "Сосуд")
class IMessageBus(ABC):
    """Абстракция для работы с очередями и стримингом."""

    @abstractmethod
    async def publish(self, topic: str, message: OctaEvent):
        """Отправляет сообщение в указанный топик."""
        pass

    @abstractmethod
    async def subscribe(self, topic: str, handler: Callable):
        """Подписывается на топик и передает сообщения в обработчик."""
        pass
