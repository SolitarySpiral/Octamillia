from app import Brain
from app.body.messaging import InMemoryMessageBus, KafkaMessageBus
from app.brain.dependency_provider import BodyServiceProvider
from app.brain.logger import logger


def brain_starter():
    print("--- 🐙 Инициализация Octamillia ---")
    # ... инициализация ...
    # 1. КОМПОЗИЦИЯ: Создание конкретных реализаций ВНЕ Провайдера
    bus_config = {
        "kafka": KafkaMessageBus(bootstrap_servers="localhost:9092"),
        "inmemory": InMemoryMessageBus(),
    }
    provider = BodyServiceProvider(logger, bus_implementations=bus_config)
    brain = Brain(body_provider=provider)
    return brain
