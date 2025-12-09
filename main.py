import asyncio
import os

from app import Brain, CommandContext
from app.body.blood import OctaEvent
from app.body.messaging import InMemoryMessageBus, KafkaMessageBus
from app.brain.dependency_provider import BodyServiceProvider
from app.brain.logger import logger
from app.tentacles import ConfigPayload, VideoPayload

# --- Глобальная инициализация ---
global_config_path = os.environ.get("OCTAMILLIA_GLOBAL_CONFIG_PATH", "./config/default.yaml")
# --------------------------------


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
    print("\n--- 📞 ТЕСТ 1.1: LOAD_CONFIG ---")
    config_context = CommandContext(
        command_name="LOAD_CONFIG",
        correlation_id="C-1",
        params={"path": "./config/config.yaml"},
        source_service="MAIN",
        user_id="SolitarySpiral",
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

    print("\n--- 📞 ТЕСТ 1.2: SET_KEY ---")
    config_context = CommandContext(
        command_name="SET_KEY",
        correlation_id="C-2",
        params={"data": {"key": "token", "value": "vk.1234"}, "path": "./config/config.yaml"},
        source_service="MAIN",
        user_id="SolitarySpiral",
    )

    result = await brain.route_command(config_context)
    print("Результат команды route_command()", result)

    if result.is_success:
        if isinstance(result.data, ConfigPayload):
            # А вот это самая мощная фича для "Вен" (Event Sourcing):
            # Мы можем одной командой превратить это в JSON для отправки в Кафку/БД
            json_data = result.model_dump_json()
            print(f"Serialized for Veins: {json_data}")
            # {"status": "SUCCESS", "message": "", "data": {"filename": "...", ...}}

    else:
        print(f"Ошибка: {result.message}")

    print("\n--- 📞 ТЕСТ 1.3: GET_KEY ---")
    config_context = CommandContext(
        command_name="GET_KEY",
        correlation_id="C-3",
        params={"key": "token", "path": "./config/config.yaml"},
        source_service="MAIN",
        user_id="SolitarySpiral",
    )

    result = await brain.route_command(config_context)
    print("Результат команды route_command()", result)

    if result.is_success:
        if isinstance(result.data, ConfigPayload):
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

    # --- ТЕСТ НОВОЙ ПАЙПЛАЙН-ТЕНТАКЛИ ---
    print("\n" + "=" * 50)
    print("🧪 ТЕСТ КОНВЕЙЕРНОЙ ТЕНТАКЛИ")
    print("=" * 50)

    # Тест 1: Успешный конвейер
    print("\n--- 📊 ТЕСТ 1: Успешная обработка ---")
    pipeline_context = CommandContext(
        command_name="PROCESS_PIPELINE",
        correlation_id="PIPE-001",
        params={"data": {"age": "25", "score": "100", "items": "5"}},
        user_id="test_user",
        source_service="TEST",
    )

    result = await brain.route_command(pipeline_context)
    print(f"Результат: {result.status}")
    if result.is_success:
        print(f"Данные после конвейера: {result.data.get('result')}")
        print(f"Метаданные: {result.data.get('metadata')}")

    # Тест 2: Ошибка валидации
    print("\n--- ⚠️ ТЕСТ 2: Ошибка валидации ---")
    bad_pipeline_context = CommandContext(
        command_name="PROCESS_PIPELINE",
        correlation_id="PIPE-002",
        params={
            "data": {
                "age": "25",
                "score": "не число",  # Ошибка здесь!
                "items": "5",
            }
        },
        user_id="test_user",
        source_service="TEST",
    )

    bad_result = await brain.route_command(bad_pipeline_context)
    print(f"Результат: {bad_result.status}")
    print(f"Сообщение: {bad_result.message}")

    # Тест 3: Проверка, что тентакля автоматически подгрузилась
    print("\n--- 🔍 ТЕСТ 3: Проверка регистрации ---")
    print(f"Зарегистрированные тентакли: {list(brain.registry.keys())}")
    print(f"Доступные команды: {list(brain.command_map.keys())}")

    if "DATA_PIPELINE" in brain.registry:
        print("✅ DATA_PIPELINE успешно зарегистрирована!")
    if "PROCESS_PIPELINE" in brain.command_map:
        print("✅ PROCESS_PIPELINE доступна для роутинга!")

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
