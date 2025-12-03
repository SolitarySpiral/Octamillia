import asyncio

from app import Brain, CommandContext
from app.body.blood import OctaEvent
from app.body.messaging import InMemoryMessageBus, KafkaMessageBus
from app.brain.dependency_provider import BodyServiceProvider
from app.brain.logger import logger
from app.tentacles import ConfigPayload, VideoPayload


async def ask_octamillia():
    print("--- 🐙 Инициализация Octamillia ---")
    # ... инициализация ...
    # 1. КОМПОЗИЦИЯ: Создание конкретных реализаций ВНЕ Провайдера
    bus_config = {
        "kafka": KafkaMessageBus(bootstrap_servers="localhost:9092"),
        "inmemory": InMemoryMessageBus(),
    }
    provider = BodyServiceProvider(logger, bus_implementations=bus_config)
    brain = Brain(body_provider=provider)

    # Запускаем сердце (оно попробует поднять и Кафку, и Память)
    await provider.get_heart().start()

    # Один раз зажигаем мозг. Щупальца подписываются на Сердце.
    # Сердце транслирует подписку и в Кафку, и в Память.
    await brain.ignite()
    await asyncio.sleep(2)
    print("\n--- ✅ Результат Обнаружения ---")
    print(f"Обнаруженные ID щупалец: {list(brain.registry.keys())}")
    print(f"Карта команд: {list(brain.command_map.keys())}")
    print("-------------------------")

    # --- ТЕСТ 1: Исполнение старой логики (LOAD_CONFIG) ---
    print("\n--- 📞 ТЕСТ 1: LOAD_CONFIG (Старый функционал) ---")
    config_context = CommandContext(
        command_name="LOAD_CONFIG",
        correlation_id="C-1",
        user_id=101,
        params={"path": "/conf/config.yaml"},
        source_service="UserAPI",
    )

    result = await brain.route_command(config_context)
    print("Результат команды route_command()", result)

    if result.is_success:
        if isinstance(result.data, ConfigPayload):
            print(f"Токен: {result.data.token}")  # <--- IDE подскажет!
            print(f"Окружение: {result.data.environment}")
            print(f"ttl: {result.data.ttl}")

            # А вот это самая мощная фича для "Вен" (Event Sourcing):
            # Мы можем одной командой превратить это в JSON для отправки в Кафку/БД
            json_data = result.model_dump_json()
            print(f"Serialized for Veins: {json_data}")
            # {"status": "SUCCESS", "message": "", "data": {"filename": "...", ...}}

    else:
        print(f"Ошибка: {result.message}")

    # --- ТЕСТ 2: Исполнение НОВОЙ логики (DOWNLOAD_VIDEO) ---
    print("\n--- 📞 ТЕСТ 2: DOWNLOAD_VIDEO (Новый функционал) ---")
    video_context = CommandContext(
        command_name="DOWNLOAD_VIDEO",
        correlation_id="V-2",
        user_id=102,
        params={"url": "http://video.com/new.mp4"},
        source_service="UserAPI",
    )

    result = await brain.route_command(video_context)
    print("Результат команды route_command()", result)

    if result.is_success:
        if isinstance(result.data, VideoPayload):
            print(f"Файл: {result.data.filename}")  # <--- IDE подскажет .filename!
            print(f"Размер: {result.data.size_mb} MB")

            # А вот это самая мощная фича для "Вен" (Event Sourcing):
            # Мы можем одной командой превратить это в JSON для отправки в Кафку/БД
            json_data = result.model_dump_json()
            print(f"Serialized for Veins: {json_data}")
            # {"status": "SUCCESS", "message": "", "data": {"filename": "...", ...}}

    else:
        print(f"Ошибка: {result.message}")

    # --- ТЕСТ 3: Проверка на несуществующую команду
    print("\n--- ✅ Проверка универсальности ---")
    unknown_context = CommandContext(
        command_name="MAKE_COFFEE", correlation_id="X-3", user_id=0, params={}, source_service="API"
    )
    result_unknown = await brain.route_command(unknown_context)
    print(
        f"[МОЗГ ВЕРНУЛ НЕИЗВЕСТНОЕ]: Статус={result_unknown.status}, Сообщение={result_unknown.message}"
    )

    # --- ТЕСТ 4: Корректная проверка асинхронного брокера ---
    print("\n--- 🩸 ТЕСТ 4: Асинхронная публикация в Сосуд (ORDER_TOPIC) ---")
    # --- ТЕСТ 4.1: InMemory ---
    print("\n--- 🩸 ТЕСТ 4.1: InMemory ---")
    event_mem = OctaEvent(event="TEST_MEM", payload={"id": "test4.1", "message": "Puck"})

    # Явно просим Сердце отправить только в память (для чистоты теста)
    await provider.get_heart().publish("ORDER_TOPIC", event_mem, target_bus="inmemory")

    await asyncio.sleep(2)

    # --- ТЕСТ 4.2: Kafka ---
    print("\n--- 🩸 ТЕСТ 4.2: Kafka ---")
    event_kafka = OctaEvent(
        event="TEST_KAFKA",
        payload={"id": "ORDER-KAFKA-1", "message": "Fuck"},  # <--- Должен быть 'id'
    )

    # Явно просим Сердце отправить только в Кафку
    # (Щупальце всё равно это получит, так как оно подписано на Сердце)
    await provider.get_heart().publish("ORDER_TOPIC", event_kafka, target_bus="kafka")

    await asyncio.sleep(2)

    # Остановка
    await provider.get_heart().stop()


if __name__ == "__main__":
    asyncio.run(ask_octamillia())
