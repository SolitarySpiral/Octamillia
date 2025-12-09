# app/suckers/validators/int_validator.py
from app.suckers.base import ISucker, SuckerContext


class IntValidatorSucker(ISucker):
    """Присоска-валидатор: проверяет, что данные - числа"""

    def get_config(self):
        return {"name": "IntValidator", "type": "validator", "version": "1.0"}

    async def process(self, context: SuckerContext) -> SuckerContext:
        data = context.data

        # Пример логики: проверяем, что все значения - числа
        for key, value in data.items():
            try:
                int(value)
            except (ValueError, TypeError):
                context.status = "ERROR"
                context.data = {"error": f"Значение '{key}'={value} не является числом"}
                return context

        # Добавляем метаданные о валидации
        context.metadata["validated"] = True
        context.metadata["validated_fields"] = list(data.keys())
        return context
