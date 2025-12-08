# === МОДЕЛИ ДАННЫХ (PAYLOADS) ===
# Это то, что будет лежать внутри data=
# Любой формат pydantic моделей
from typing import Any, Dict

from pydantic import BaseModel, ConfigDict


class ConfigPayload(BaseModel):
    # 1. Поля, которые вы контролируете и хотите валидировать
    command_params: Dict[str, Any]

    # 2. Разрешаем любые другие поля (kwargs)
    model_config = ConfigDict(extra="allow")
