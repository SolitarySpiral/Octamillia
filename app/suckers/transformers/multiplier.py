# app/suckers/transformers/multiplier.py
from app.suckers.base import ISucker, SuckerContext


class MultiplierSucker(ISucker):
    """Присоска-трансформер: умножает все числа на заданный коэффициент"""

    def __init__(self, factor: int = 2):
        self.factor = factor

    def get_config(self):
        return {
            "name": "Multiplier",
            "type": "transformer",
            "factor": self.factor,
            "version": "1.0",
        }

    async def process(self, context: SuckerContext) -> SuckerContext:
        data = context.data

        # Умножаем все числовые значения
        transformed = {}
        for key, value in data.items():
            try:
                transformed[key] = int(value) * self.factor
            except (ValueError, TypeError):
                transformed[key] = value  # Оставляем как есть, если не число

        context.data = transformed
        context.metadata[f"multiplied_by_{self.factor}"] = True
        return context
