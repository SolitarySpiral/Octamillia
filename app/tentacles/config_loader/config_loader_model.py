# === МОДЕЛИ ДАННЫХ (PAYLOADS) ===
# Это то, что будет лежать внутри data=
# Любой формат pydantic моделей
from pydantic import BaseModel


class ConfigPayload(BaseModel):
    token: str
    ttl: int
    environment: str
