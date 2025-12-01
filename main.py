import asyncio

from app import Brain, CommandContext
from app.tentacles import ConfigPayload, VideoPayload


async def ask_octamillia():
    print("--- 🐙 Инициализация Octamillia ---")

    # Мозг запускается и сам находит все щупальца
    brain = Brain()
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

    print("\n--- ✅ Проверка универсальности ---")
    unknown_context = CommandContext(
        command_name="MAKE_COFFEE", correlation_id="X-3", user_id=0, params={}, source_service="API"
    )
    result_unknown = await brain.route_command(unknown_context)
    print(
        f"[МОЗГ ВЕРНУЛ НЕИЗВЕСТНОЕ]: Статус={result_unknown.status}, Сообщение={result_unknown.message}"
    )


if __name__ == "__main__":
    asyncio.run(ask_octamillia())
