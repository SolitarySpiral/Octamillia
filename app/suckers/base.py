# app/suckers/base.py
from abc import ABC, abstractmethod
from typing import Any, Dict

from pydantic import BaseModel


class SuckerContext(BaseModel):
    """Контекст данных, передаваемый между присосками"""

    data: Dict[str, Any]  # Обработанные данные
    metadata: Dict[str, Any]  # Метаданные конвейера
    status: str = "PROCESSING"  # PROCESSING, SUCCESS, ERROR


class ISucker(ABC):
    """Контракт присоски"""

    @abstractmethod
    async def process(self, context: SuckerContext) -> SuckerContext:
        """Обработать порцию данных"""
        pass

    @abstractmethod
    def get_config(self) -> Dict[str, Any]:
        """Конфигурация присоски (что умеет, параметры и т.д.)"""
        pass
