# app/brain/external_client.py (Новый файл: Модель RPC-клиента)
from typing import Any

import httpx

from .models import OctaResponse
from .WAI import CommandContext


class ExternalTentacleClient:
    """
    Класс, который Мозг использует для общения с внешним щупальцем.
    Он знает адрес, но не знает, что там внутри (K8s, ЦОД и т.д.).
    """

    def __init__(self, tentacle_url: str):
        self.url = tentacle_url  # IP:port или DNS-имя

    async def process_command(self, context: CommandContext) -> OctaResponse[Any]:
        # !!! Здесь происходит магия !!!
        # Вместо вызова метода класса, это делает HTTP POST/gRPC call на self.url

        # Пример: имитация сетевого вызова
        response = await httpx.post(f"{self.url}/command", json=context.model_dump())

        # Валидация ответа по контракту OctaResponse, пришедшему по сети
        return OctaResponse.model_validate_json(response.text)

    async def get_health(self) -> float:
        # Мозг просто опрашивает публичный Health Check Endpoint
        response = await httpx.get(f"{self.url}/health")
        if response.status_code == 200:
            return 1.0
        return 0.0
