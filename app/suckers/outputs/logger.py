# app/suckers/outputs/logger.py
from app.suckers.base import ISucker, SuckerContext


class LoggerSucker(ISucker):
    """Присоска-логгер: логирует состояние данных"""

    def get_config(self):
        return {"name": "Logger", "type": "output", "version": "1.0"}

    async def process(self, context: SuckerContext) -> SuckerContext:
        print(f"[LoggerSucker] Текущие данные: {context.data}")
        print(f"[LoggerSucker] Метаданные: {context.metadata}")
        print(f"[LoggerSucker] Статус: {context.status}")

        # Добавляем метку о логировании
        context.metadata["logged_at"] = "some_timestamp"
        return context
