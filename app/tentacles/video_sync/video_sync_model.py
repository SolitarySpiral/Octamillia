# === МОДЕЛИ ДАННЫХ (PAYLOADS) ===
# Это то, что будет лежать внутри data=
# Любой формат pydantic моделей
from pydantic import BaseModel


class VideoPayload(BaseModel):
    filename: str
    size_mb: float
    duration: int
    path: str
