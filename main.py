import asyncio

from app import Brain, CommandContext
from app.body.blood import OctaEvent
from app.brain.dependency_provider import BodyServiceProvider
from app.brain.logger import logger
from app.tentacles import ConfigPayload, VideoPayload


async def ask_octamillia():
    print("--- 🐙 Инициализация Octamillia ---")
    # 2. Создаем Провайдера
    provider = BodyServiceProvider(
        logger_instance=logger,
        # config_reader_instance=main_config
    )
    # Мозг запускается и сам находит все щупальца
    brain = Brain(body_provider=provider)
    # ВАЖНО: Мы зажигаем мозг асинхронно!
    await brain.ignite()

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

    # 1. Получаем доступ к активному Сосуду (Message Bus)
    #    (Предполагаем, что BodyServiceProvider передан в Brain и имеет метод get_message_bus)
    try:
        message_bus = brain.body_provider.get_message_bus()
    except AttributeError:
        print(
            "[ОШИБКА ТЕСТА]: BodyServiceProvider не был инициализирован или не имеет get_message_bus."
        )
        # Здесь нужно выйти или исправить инициализацию
        exit(1)

    # 2. Создаем "Кровяное тельце" (OctaEvent)
    order_event = OctaEvent(
        event="NEW_ORDER", payload={"id": "ORDER-999", "symbol": "AAPL", "quantity": 10}
    )

    # 3. Публикуем его в Топик (ВЕНА)
    #    Это вызовет _handle_incoming_order в BrokerageTentacle
    await message_bus.publish("ORDER_TOPIC", order_event)

    # 4. Даем время асинхронному слушателю на обработку
    await asyncio.sleep(0.1)
    print("[ТЕСТ УСПЕШЕН]: Проверка консоли. Сообщение должно было быть обработано.")

    # Проверка консоли должна показать:
    # [BUS] 📥 Сообщение 'NEW_ORDER' получено из 'ORDER_TOPIC'.
    # [BrokerageTentacle] Получен новый ордер: {'id': 'ORDER-999', ...}
    # [BUS] 📤 Сообщение 'ORDER_RECEIVED' отправлено в топик 'INTERNAL_FEEDBACK'.


if __name__ == "__main__":
    asyncio.run(ask_octamillia())
