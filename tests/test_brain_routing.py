import pytest

from app import Brain, CommandContext
from app.brain import BodyServiceProvider
from app.brain.logger import logger
from app.tentacles import ConfigPayload

# Import Brain and Payloads as they are exported for the clean API


@pytest.fixture(scope="module")
async def initialized_brain():
    """Фикстура, которая инициализирует и зажигает Мозг один раз."""
    provider = BodyServiceProvider(
        logger_instance=logger,
        # config_reader_instance=main_config
    )
    # Мозг запускается и сам находит все щупальца
    brain = Brain(body_provider=provider)
    await brain.ignite()
    return brain


@pytest.mark.asyncio
async def test_brain_routes_config_loader(initialized_brain):
    # Проверяем, что Мозг отправляет команду LOAD_CONFIG нужному щупальцу
    context = CommandContext(
        command_name="LOAD_CONFIG",
        correlation_id="C-1",
        user_id=101,
        params={"path": "/conf/config.yaml"},
        source_service="UserAPI",
    )

    result = await initialized_brain.route_command(context)

    assert result.is_success is True
    assert isinstance(result.data, ConfigPayload)


@pytest.mark.asyncio
async def test_brain_handles_unknown_command(initialized_brain):
    # Проверяем универсальную обработку неизвестной команды
    context = CommandContext(
        command_name="MAKE_COFFEE", correlation_id="X-3", user_id=0, params={}, source_service="API"
    )

    result = await initialized_brain.route_command(context)

    assert result.is_success is False
    assert "неизвестна в Геноме WAI" in result.message  # Или другое ожидаемое сообщение об ошибке
