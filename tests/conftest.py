# tests/conftest.py

import sys
from pathlib import Path

# Определяем корень проекта, независимо от того, где запущен pytest.
# Path(__file__).parent.parent ведет из 'tests/conftest.py' к 'Octamillia/'
PROJECT_ROOT = Path(__file__).parent.parent

# Добавляем корень проекта в начало sys.path.
# Это гарантирует, что Brain, запущенный в тесте,
# будет видеть корень проекта как отправную точку.
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# ВАЖНО: Мы также можем исправить проблему с sys.path[0] для логики directory_scanner
# Хотя insert(0) обычно достаточно, явное удаление 'tests/' из пути
# помогает избежать путаницы, если Brain использует sys.path[0].
# sys.path.pop(1) # Если 'tests' добавился вторым, что часто происходит.
