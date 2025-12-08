from typing import Any, Dict, Generic, Optional, TypeVar

from pydantic import BaseModel, Field

# Определение дженерик-типа (Заполнитель)
DataT = TypeVar("DataT")


# === УНИВЕРСАЛЬНЫЙ ОТВЕТ (КОНВЕРТ) ===
class OctaResponse(BaseModel, Generic[DataT]):
    """
    Универсальный типизированный ответ архитектуры Octamillia

    Метод ok возвращает класс OctaResponse(status="SUCCESS", data=data, message=msg)
    если заполнено, ещё сообщение.
    Метод fail возвращает класс OctaResponse(status="ERROR", data=None, message=msg)
    """

    status: str = Field(..., description="SUCCESS, ERROR, WARNING")
    message: str = Field(default="", description="Описание ошибки или детали")
    # Магия здесь: data имеет тип DataT, который подставится автоматически
    data: Optional[DataT] = None
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Дополнительные метаданные ответа"
    )

    @property
    def is_success(self) -> bool:
        return self.status == "SUCCESS"

    # Фабричные методы для красоты кода
    @classmethod
    def ok(cls, data: DataT, msg: str = "", **kwargs: Any):
        return cls(status="SUCCESS", data=data, message=msg, metadata=kwargs)

    @classmethod
    def fail(cls, msg: str = "", **kwargs: Any):
        return cls(status="ERROR", data=None, message=msg, metadata=kwargs)
