# app/brain/brain.py
import importlib
from pathlib import Path
from typing import Any, Dict, List

from .dependency_provider import BodyServiceProvider
from .external_client import ExternalTentacleClient
from .logger import logger
from .models import OctaResponse
from .WAI import (
    WAI_REGISTRY,
    CommandContext,
    CommandDispatchTentacle,
    TentacleMetadata,
)


class Brain:
    """
    Мозг (Control Plane) Octamillia. Отвечает за маршрутизацию и реконсиляцию.
    """

    def __init__(self, body_provider: BodyServiceProvider):
        self.registry = WAI_REGISTRY
        self.active_external_tentacles: Dict[str, ExternalTentacleClient] = {}
        self.last_used_index: Dict[str, int] = {}
        self.command_map = {}  # Карта пока пуста
        self.body_provider = body_provider

    async def ignite(self):
        """
        Метод 'Зажигания'.
        Асинхронно сканирует геном и активирует синапсы (строит карты).
        """
        print("\n🔥 [BRAIN]: Зажигание нейросетей (Ignition)...")

        # 1. Запуск Discovery (теперь мы можем использовать await!)
        await self._discover_tentacles(directory_scanner())

        # 2. Построение карты команд
        self.command_map = self._build_command_map()
        print(f"🔥 [BRAIN]: Мозг активен. Доступные команды: {list(self.command_map.keys())}")

    async def _discover_tentacles(self, module_paths: List[str]):
        """Асинхронная загрузка и опрос щупалец."""

        common_deps = self.body_provider.get_common_dependencies()

        for module_path in module_paths:
            try:
                module = importlib.import_module(module_path)

                if hasattr(module, "TENTACLE_METADATA"):
                    metadata = module.TENTACLE_METADATA
                    if metadata.tentacle_id not in self.registry:
                        self.registry[metadata.tentacle_id] = metadata
                        # 1. Создаем Инстанс Щупальца, используя инжекцию!
                        # ДОБАВЛЕНИЕ: Передаем tentacle_id как зависимость
                        common_deps["tentacle_id"] = metadata.tentacle_id
                        # Передаем **common_deps** в конструктор
                        instance = metadata.internal_implementation(**common_deps)

                        # 3. Принятие оферов обычных щупалец
                        metadata.handles_commands = instance.get_capabilities()
                        # 2. Мозг также должен настроить асинхронные подписки
                        await self._activate_async_subscriptions(instance)

                        print(
                            f"  [BRAIN DISCOVERY]: Офер принят: {metadata.tentacle_id} {metadata.handles_commands}"
                        )
            except ModuleNotFoundError:
                pass
            except Exception as e:
                logger.exception(e)
                print(f"  [BRAIN DISCOVERY ERROR]: {module_path}: {e}")

    def _build_command_map(self) -> Dict[str, List[str]]:
        """Строит карту: КОМАНДА -> [ID щупалец, которые могут ее обработать]."""
        cmap = {}
        for meta in self.registry.values():
            for cmd in meta.handles_commands:
                if cmd not in cmap:
                    cmap[cmd] = []
                cmap[cmd].append(meta.tentacle_id)
        return cmap

    def initiate_regeneration(self, tentacle_id: str):
        """Паттерн Регенерации: Мозг дает команду Телу отрастить новое щупальце."""
        # Только если это внешняя тентакля
        if tentacle_id in self.active_external_tentacles:
            print(f"  [BRAIN]: Инициирую регенерацию {tentacle_id}...")
        # Здесь была бы команда к Kubernetes/Docker на запуск нового Pod

    def _get_standin_instance(self, metadata: TentacleMetadata) -> CommandDispatchTentacle:
        """
        Получает и инициализирует Standin (Внутреннее Щупальце) из репозитория app.tentacles.
        """
        if not metadata.internal_implementation:
            raise ValueError(
                f"WAI Error: Для {metadata.tentacle_id} не найдена Standin-реализация!"
            )

        # Возвращаем инстанс, который будет выполнять работу
        return metadata.internal_implementation()

    async def route_command(self, context: CommandContext) -> OctaResponse[Any]:
        """Основной роутер: ищет щупальце, переключается на Standin при необходимости."""

        command = context.command_name

        if command not in self.command_map:
            return OctaResponse.fail(f"Команда {command} неизвестна в Геноме WAI.")

        # 1. Получаем ВСЕ ID щупалец, способных обработать команду
        tentacle_ids = self.command_map[command]
        total_count = len(tentacle_ids)

        # Определяем начальный индекс для Round Robin
        start_index = self.last_used_index.get(command, 0)

        # --- ФАЗА 1: ПОИСК АКТИВНОГО И ЗДОРОВОГО ВНЕШНЕГО ЩУПАЛЬЦА (Data Plane) ---

        # Циклический обход всех щупалец, начиная с последнего использованного
        for i in range(total_count):
            # Вычисляем текущий индекс циклически
            current_index = (start_index + i) % total_count
            t_id = tentacle_ids[current_index]
            # t_id - это ID, который может быть либо типом, либо конкретным запущенным инстансом

            # Проверяем, есть ли для этого ID активный RPC-клиент
            if t_id in self.active_external_tentacles:
                client = self.active_external_tentacles[t_id]

                try:
                    # Проверяем пульс (сетевой вызов)
                    health = await client.get_health()
                except Exception as e:
                    # Сетевая ошибка (таймаут, DNS-ошибка) - щупальце недоступно
                    print(f"[BRAIN]: Внешнее щупальце {t_id} недоступно по сети. Ошибка: {e}")
                    # Запускаем регенерацию, чтобы его восстановить, и пробуем следующее
                    self.initiate_regeneration(t_id)
                    continue

                if health >= 1.0:
                    # Успех: Найдено здоровое внешнее щупальце
                    self.last_used_index[command] = (current_index + 1) % total_count
                    print(f"[BRAIN]: Роутинг на здоровое ВНЕШНЕЕ Щупальце ({t_id}).")
                    return await client.process_command(context)
                else:
                    # Щупальце доступно, но нездорово (например, БД недоступна)
                    print(
                        f"[BRAIN]: Внешнее щупальце {t_id} нездорово (Health: {health}).\
                            Инициирую Регенерацию."
                    )
                    self.initiate_regeneration(t_id)
                    # И пробуем следующее щупальце в списке
            else:
                print(f"[DEBUG]: Щупальце {t_id} - это standin, внешнего клиента нет")
        print(f"[BRAIN]: Внешние щупальца для {command} недоступны. Переключаюсь на STANDIN.")

        tentacle_id = tentacle_ids[0]
        metadata = self.registry[tentacle_id]

        standin_instance = self._get_standin_instance(metadata)
        self.initiate_regeneration(tentacle_id)

        # Standin всегда возвращает OctaResponse
        return await standin_instance.process_command(context)

    async def _activate_async_subscriptions(self, instance: CommandDispatchTentacle):
        """Автоматически подписывает методы инстанса на шину сообщений."""

        # ИСПРАВЛЕНИЕ: Берем главную шину (Сердце) у Провайдера
        # (Предполагаем, что get_common_dependencies возвращает 'message_bus')
        # Либо добавим метод get_main_bus() в провайдер.

        # Вариант А: Если провайдер отдает HeartBus как message_bus в common_dependencies
        deps = self.body_provider.get_common_dependencies()
        message_bus = deps.get("message_bus")

        # Вариант Б (Надежнее): Явный метод в провайдере
        # message_bus = self.body_provider.get_main_bus()

        if not message_bus:
            print("  [BRAIN WARNING]: Шина сообщений не найдена для подписки.")
            return

        handlers = instance.get_event_handlers()

        for topic, method_name in handlers.items():
            handler_method = getattr(instance, method_name)

            # Теперь подписка идет в СЕРДЦЕ -> которое подписывает И Kafka, И Memory
            await message_bus.subscribe(topic, handler_method)

            print(f"  [BRAIN ASYNCSYNC]: Подписка {instance.tentacle_id}.{method_name} -> {topic}")


# =======================================================
# Discovery Service (Целевое решение: сканирование ФС)
# =======================================================
def directory_scanner(base_dir: str = "app.tentacles") -> List[str]:
    """
    Сканирует целевой каталог для поиска потенциальных модулей Щупалец.
    Использует нативный функционал OS (pathlib).
    """
    # В этой среде мы не можем выполнять os.walk, но это целевая логика:
    # -----------------------------------------------------------------
    import os

    module_names = []

    app_spec = importlib.util.find_spec("app")
    if app_spec is None or app_spec.origin is None:
        raise RuntimeError("Не удалось найти пакет 'app' для сканирования.")
    app_dir = Path(app_spec.origin).parent.parent
    base_path = Path(app_dir) / base_dir.replace(".", "/")  # Путь к app/tentacles

    print(f"\n  [DISCOVERY SERVICE]: Сканирую целевой каталог: {base_path}...")
    for root, _, files in os.walk(base_path):
        for file in files:
            if file.endswith(".py") and file != "__init__.py":
                # Преобразование пути в имя модуля для importlib
                relative_path = Path(root).relative_to(app_dir)
                module_name = relative_path.joinpath(file[:-3]).as_posix().replace("/", ".")
                module_names.append(module_name)

    print(f"\n  [DISCOVERY SERVICE]: Обнаружены следующие компоненты: {module_names}")
    return module_names
