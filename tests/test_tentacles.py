import pytest

from app.brain import CommandContext
from app.tentacles import (
    ConfigLoaderStandinTentacle,
    ConfigPayload,  # Предполагаем, что payload экспортирован
)

# Используем прямой путь к классу для Unit-теста


# 1. Фикстура: Создаем контекст команды для теста
@pytest.fixture
def load_config_context():
    """Создает контекст, необходимый для успешной загрузки конфига."""
    return CommandContext(
        command_name="LOAD_CONFIG",
        correlation_id="TEST-C-1",
        user_id=999,
        params={"path": "/conf/test.yaml"},
        source_service="TEST_RUNNER",
    )


# 2. Тестовая функция
@pytest.mark.asyncio  # Используется, если у вас установлен pytest-asyncio
async def test_config_loader_success(load_config_context):
    # Аранжировка (Arrange): Создаем экземпляр тестируемого класса
    tentacle = ConfigLoaderStandinTentacle()

    # Действие (Act): Вызываем тестируемый метод
    response = await tentacle.process_command(load_config_context)

    # Проверка (Assert): Проверяем результат
    assert response.status == "SUCCESS"
    assert response.is_success is True
    assert isinstance(response.data, ConfigPayload)
    assert response.data.environment == "окружение дев"
    assert response.data.token == "Секретный_токен"


@pytest.mark.asyncio
async def test_config_loader_unsupported_command():
    # Проверяем, что щупальце не обрабатывает неизвестную команду
    # Теперь CommandContext содержит все обязательные поля
    context = CommandContext(
        command_name="INVALID_COMMAND",
        correlation_id="Test-X-4",  # <--- Добавлено
        user_id=1,  # <--- Добавлено
        params={},
        source_service="Test",  # <--- Добавлено
    )
    tentacle = ConfigLoaderStandinTentacle()

    response = await tentacle.process_command(context)

    assert response.status == "ERROR"
    assert "is not supported" in response.message
