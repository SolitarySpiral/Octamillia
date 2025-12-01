# app/__init__.py

# 1. Экспортируем ключевые сущности из подпакетов:
# Это позволяет писать: 'from app import BodyCore' вместо 'from app.body import BodyCore'

from .brain import Brain, CommandContext

# 2. Определение __all__
# Это явно указывает, какие объекты доступны при импорте 'from app import *'
__all__ = [
    "Brain",
    "CommandContext",
]

# 3. Версионирование (метаданные)
__version__ = "1.0.0"
