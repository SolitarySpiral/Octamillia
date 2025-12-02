# app/body/blood.py
from typing import Generic, Optional, TypeVar

from pydantic import BaseModel, Field

# Определение дженерик-типа (Заполнитель)
DataT = TypeVar("DataT")


# === УНИВЕРСАЛЬНЫЙ ИВЕНТ (кроваяное тельце) ===
class OctaEvent(BaseModel, Generic[DataT]):
    event: str = Field(..., description="Any named event type")
    payload: Optional[DataT] = None
