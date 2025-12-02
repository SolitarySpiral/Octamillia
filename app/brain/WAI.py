# ========/========
# Геном Octamillia
# =======/=========
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Type

from pydantic import BaseModel, Field

from .models import OctaResponse


# =======================================================
# 1. Язык общения (Артерии/Вены)
# =======================================================
class CommandContext(BaseModel):
    """Универсальный контекст команды, передаваемый по Артериям."""

    command_name: str = Field(..., description="Имя команды")
    correlation_id: str = Field(..., description="Ключ идемпотентности / ID транзакции")
    user_id: Optional[int]
    params: Dict[str, Any]
    # ... другие метаданные для маршрутизации
    source_service: Optional[str]


# =======================================================
# 2. Универсальный Контракт (The Plug/Socket)
# =======================================================
class TentacleContract(ABC):
    """
    Базовый контракт, который должен реализовать ЛЮБОЙ модуль.
    Это 'штекер', который подключается к 'розетке' Мозга.

    Новый класс щупальца должен его наследовать.\n
    Новый класс должен реализовать следующие методы\n
    async def process_command(self, context: CommandContext) -> OctaResponse[Any]\n
    async def get_capabilities(self) -> List[str]\n
    async def get_health(self) -> float
    """

    @abstractmethod
    async def process_command(self, context: CommandContext) -> OctaResponse[Any]:
        """Основной метод исполнения логики по команде."""
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def get_capabilities(cls) -> List[str]:
        """Метод, который сообщает Мозгу: 'Я умею делать X, Y, Z'."""
        raise NotImplementedError

    @abstractmethod
    async def get_health(self) -> float:
        """Пульс Щупальца."""
        raise NotImplementedError


class CommandDispatchTentacle(TentacleContract, ABC):
    """
    Базовый класс, который реализует process_command и get_capabilities
    через универсальный Паттерн Диспетчер Команд.
    """

    # ----------------------------------------------------
    # АБСТРАКТНЫЕ ЭЛЕМЕНТЫ (Должны быть реализованы дочерним классом)
    # ----------------------------------------------------
    _COMMAND_HANDLERS: Dict[str, str] = {}
    # НОВЫЙ КОНТРАКТ: Для асинхронных событий (подписывается Мозгом на шину)
    # Ключ: Имя Топика/События (вена/артерия). Значение: Имя метода-обработчика.
    _EVENT_HANDLERS: Dict[str, str] = {}

    def __init__(self, **kwargs):
        # Базовый класс принимает любые аргументы инъекции
        # и сохраняет их как атрибуты (например, tentacle_id)
        for key, value in kwargs.items():
            setattr(self, key, value)

    @classmethod
    def get_event_handlers(cls) -> Dict[str, str]:
        """Мозг использует этот метод для обнаружения подписок."""
        return cls._EVENT_HANDLERS

    # ----------------------------------------------------
    # УНИВЕРСАЛЬНАЯ ЛОГИКА (Не требует переопределения)
    # ----------------------------------------------------
    @property
    def _command_handlers(self) -> Dict[str, Callable]:
        # 2. ДИНАМИЧЕСКАЯ РЕАЛИЗАЦИЯ (для process_command, вызывается при вызове)
        # Связываем строки с методами экземпляра
        return {
            cmd_name: getattr(self, method_name)
            for cmd_name, method_name in self._COMMAND_HANDLERS.items()
        }

    @classmethod
    def get_capabilities(cls) -> List[str]:
        """Метод, который сообщает Мозгу: 'Я умею делать X, Y, Z'."""
        return list(cls._COMMAND_HANDLERS.keys())

    async def process_command(self, context: CommandContext) -> OctaResponse[Any]:
        """Универсальная реализация диспетчеризации (использует свойство-геттер)."""
        handler = self._command_handlers.get(context.command_name)

        # ... (логика вызова обработчика) ...
        if handler:
            return await handler(context)

        return OctaResponse.fail(
            f"Command '{context.command_name}' is not supported by this Tentacle's dispatcher."
        )


# =======================================================
# 3. Регистрационные Метаданные
# =======================================================
@dataclass
class TentacleMetadata:
    """
    Структура данных для регистрации нового Щупальца в Реестре.
    Описывает НЕ ФУНКЦИОНАЛ, а МЕХАНИЗМ ЗАПУСКА.
    т.е. после создания функционала тентакли, которая наследует CommandDispatchTentacle,
    нужно создать оффер metadata в том же модуле.
    ВАЖНО: Мозг или процесс инициализации системы загружает этот файл
    и добавляет метаданные в глобальный WAI_REGISTRY!
    """

    tentacle_id: str  # Уникальный ID экземпляра/типа (например, 'VIDEO_DOWNLOADER_1')
    contract_interface: Type[
        CommandDispatchTentacle
    ]  # Ссылка на базовый контракт WAI (всегда CommandDispatchTentacle)

    # ----------------------------------------------------
    # Механизм реализации (WAI Core)
    # ----------------------------------------------------
    internal_implementation: Optional[Type]  # Ссылка на Standin-класс (для Тела)
    external_image_tag: Optional[str]  # Тэг Docker-образа (для внешних масштабируемых Щупалец)

    # Фактические команды, которые щупальце обещает обрабатывать
    handles_commands: List[str] = Field(default_factory=list)


# =======================================================
# 4. РЕЕСТР WAI (Динамический список возможностей)
# =======================================================
# Этот словарь будет заполнен в рантайме. Изначально пуст.
WAI_REGISTRY: Dict[str, TentacleMetadata] = {}

# Реестр команд -> ID щупалец (для быстрого роутинга)
COMMAND_MAP: Dict[str, List[str]] = {}
