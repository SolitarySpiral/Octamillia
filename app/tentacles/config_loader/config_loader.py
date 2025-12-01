# =======================================================
# app/tentacles/config_loader.py (Standin 1)
# =======================================================

import asyncio

from pybreaker import CircuitBreaker  # Используем библиотеку Circuit Breaker

from app.brain import (
    CommandContext,
    CommandDispatchTentacle,
    OctaResponse,
    TentacleMetadata,
)

from .config_loader_model import ConfigPayload

# Инициализируем выключатель для этого щупальца
# failure_threshold=5: Сломается после 5 сбоев
# reset_timeout=30: Попробует снова через 30 секунд
config_breaker = CircuitBreaker(fail_max=5, reset_timeout=30)


class ConfigLoaderStandinTentacle(CommandDispatchTentacle):
    """Исполняет логику загрузки конфигов."""

    # 1. ПЕРЕНОС ДИСПЕТЧЕРА НА УРОВЕНЬ КЛАССА
    _COMMAND_HANDLERS = {
        "LOAD_CONFIG": "_load_config",  # Обратите внимание: сохраняем только имя метода
        # ... и так далее
    }

    @config_breaker
    async def _load_config(self, context: CommandContext) -> OctaResponse[ConfigPayload]:
        print(f"  [STANDIN: ConfigLoader]: Загружаю конфиг по пути: {context.params['path']}...")
        await asyncio.sleep(0.01)
        payload = ConfigPayload(token="Секретный_токен", ttl=123, environment="окружение дев")
        return OctaResponse.ok(data=payload)

    async def get_health(self) -> float:
        return 1.0


TENTACLE_METADATA = TentacleMetadata(
    tentacle_id="CONFIG_LOADER",
    contract_interface=CommandDispatchTentacle,
    internal_implementation=ConfigLoaderStandinTentacle,
    external_image_tag="octamillia/config_loader:v1.0",
    handles_commands=ConfigLoaderStandinTentacle.get_capabilities(),
)
