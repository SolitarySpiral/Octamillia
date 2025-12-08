# =======================================================
# app/tentacles/config_loader.py (Standin 1)
# =======================================================

import asyncio
import hashlib
import json
import re
from pathlib import Path
from typing import Any, Dict, Union

import aiofiles
import yaml
from pybreaker import CircuitBreaker  # Используем библиотеку Circuit Breaker

from app.brain import (
    CommandContext,
    CommandDispatchTentacle,
    OctaResponse,
    TentacleMetadata,
)
from app.brain.logger import logger

from .config_loader_model import ConfigPayload

# Инициализируем выключатель для этого щупальца
# failure_threshold=5: Сломается после 5 сбоев
# reset_timeout=30: Попробует снова через 30 секунд
config_breaker = CircuitBreaker(fail_max=5, reset_timeout=30)
PathLike = Union[str, Path]


class ConfigLoaderStandinTentacle(CommandDispatchTentacle):
    """Исполняет логику загрузки конфигов."""

    # 1. ПЕРЕНОС ДИСПЕТЧЕРА НА УРОВЕНЬ КЛАССА
    _COMMAND_HANDLERS = {
        "LOAD_CONFIG": "_load_config",  # Обратите внимание: сохраняем только имя метода
        # "SAVE_CONFIG": "_save_config",
        "GET_KEY": "_get_key",
        "SET_KEY": "_set_key",
    }

    def __init__(self, **kwargs):
        # **kwargs захватит все, что передал Мозг (logger, message_bus и т.д.)
        # Вам нужно вызвать конструктор базового класса, чтобы он обработал эти зависимости
        super().__init__(**kwargs)

    @config_breaker
    async def _load_config(self, context: CommandContext) -> OctaResponse[ConfigPayload]:
        cfg_pth = context.params.get("path")
        if not cfg_pth:
            logger.error("Ошибка: не указан путь в конфиг в LOAD_CONFIG")
            return OctaResponse.fail("Ошибка: не указан путь в конфиг в LOAD_CONFIG")
        print(f"  [STANDIN: ConfigLoader]: Загружаю конфиг по пути: {cfg_pth}...")
        config = self.load(cfg_pth)
        await asyncio.sleep(1)
        payload = ConfigPayload(
            command_params=context.params,
            token=config.get("token", "Секретный токен"),
            ttl=config.get("ttl", "123456"),
            environment=config.get("environment", "дев"),
        )
        return OctaResponse.ok(
            data=payload,
            command_name=context.command_name,
            correlation_id=context.correlation_id,  # Полезно для трассировки
        )

    @config_breaker
    async def _resave_config(self, context: CommandContext) -> OctaResponse[ConfigPayload]:
        """Перезаписывает конфиг на конкретные данные"""
        cfg_pth = context.params.get("path")
        data = context.params.get("data")
        if not cfg_pth:
            logger.error("Ошибка: не указан путь в конфиг в SAVE_CONFIG")
            return OctaResponse.fail("Ошибка: не указан путь в конфиг в SAVE_CONFIG")
        if not data:
            logger.error("Ошибка: Сохранять нечего")
            return OctaResponse.fail("Ошибка: Сохранять нечего в SAVE_CONFIG")
        print(f"  [STANDIN: ConfigLoader]: Сохраняю конфиг по пути: {cfg_pth}...")
        self.save(data, cfg_pth)
        await asyncio.sleep(1)
        payload = ConfigPayload(
            command_params=context.params,
        )
        return OctaResponse.ok(
            data=payload,
            command_name=context.command_name,
            correlation_id=context.correlation_id,  # Полезно для трассировки
        )

    @config_breaker
    async def _get_key(self, context: CommandContext) -> OctaResponse[ConfigPayload]:
        key = context.params.get("key")
        default = context.params.get("default")
        cfg_pth = context.params.get("path")
        if not key:
            logger.error("Ошибка: не указан ключ настройки в GET_KEY")
            return OctaResponse.fail("Ошибка: не указан ключ настройки в GET_KEY")
        if not cfg_pth:
            logger.error("Ошибка: не указан путь в конфиг в GET_KEY")
            return OctaResponse.fail("Ошибка: не указан путь в конфиг в GET_KEY")

        # ИСПРАВЛЕНИЕ 1: Корректный лог
        print(f"  [STANDIN: ConfigLoader]: Загружаю ключ '{key}' по пути: {cfg_pth}...")

        # ИСПРАВЛЕНИЕ 2: Корректный вызов с тремя аргументами (path, key, default)
        key_value = self.get_key(cfg_pth, key, default)

        await asyncio.sleep(1)
        payload = ConfigPayload(
            command_params=context.params,
            value=key_value if key_value else default,
            # НЕобязательные поля, которые могут появиться в будущем:
            # my_unknown_field="hello",
            # another_data=123
            # Pydantic их примет благодаря extra='allow'
        )
        return OctaResponse.ok(
            data=payload,
            command_name=context.command_name,
            correlation_id=context.correlation_id,  # Полезно для трассировки
        )

    @config_breaker
    async def _set_key(self, context: CommandContext) -> OctaResponse[ConfigPayload]:
        data_dict = context.params.get("data")
        cfg_pth = context.params.get("path")
        if not data_dict:
            logger.error("Ошибка: не указаны настройки в SET_KEY")
            return OctaResponse.fail("Ошибка: не указан ключ настройки в SET_KEY")
        if not cfg_pth:
            logger.error("Ошибка: не указан путь в конфиг в SET_KEY")
            return OctaResponse.fail("Ошибка: не указан путь в конфиг в SET_KEY")

        print(f"  [STANDIN: ConfigLoader]: обновляю настройки по пути: {cfg_pth}...")
        print(data_dict)
        self.set_key(data_dict, cfg_pth)

        await asyncio.sleep(1)
        payload = ConfigPayload(
            command_params=context.params,
            # НЕобязательные поля, которые могут появиться в будущем:
            # my_unknown_field="hello",
            # another_data=123
            # Pydantic их примет благодаря extra='allow'
        )
        return OctaResponse.ok(
            data=payload,
            command_name=context.command_name,
            correlation_id=context.correlation_id,  # Полезно для трассировки
        )

    def load(self, config_path: PathLike) -> Dict[str, Any]:
        config_path = Path(config_path)
        if not config_path.exists():
            return {}
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                if config_path.suffix in (".yaml", ".yml"):
                    return yaml.safe_load(f) or {}
                elif config_path.suffix == ".json":
                    return json.load(f) or {}
        except Exception as e:
            logger.error(f"Не удалось загрузить конфиг {config_path}: {e}")
            return {}
        return {}

    def save(self, data: Dict[str, Any], config_path: PathLike) -> None:
        config_path = Path(config_path)
        FileUtils.ensure_dir(config_path.parent)
        try:
            with open(config_path, "w", encoding="utf-8") as f:
                if config_path.suffix in (".yaml", ".yml"):
                    yaml.safe_dump(data, f, allow_unicode=True)
                elif config_path.suffix == ".json":
                    json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Не удалось сохранить конфиг {config_path}: {e}")

    def get_key(self, key: str, path: PathLike, default: Any = None) -> Any:
        return self.load(path).get(key, default)

    def set_key(self, data: Dict[str, Any], path: PathLike) -> None:
        cfg = self.load(path)
        print(cfg)
        cfg.update(data)
        print(cfg)
        # cfg[key] = value
        self.save(cfg, path)

    async def get_health(self) -> float:
        return 1.0


TENTACLE_METADATA = TentacleMetadata(
    tentacle_id="CONFIG_LOADER",
    contract_interface=CommandDispatchTentacle,
    internal_implementation=ConfigLoaderStandinTentacle,
    external_image_tag="octamillia/config_loader:v1.0",
    handles_commands=ConfigLoaderStandinTentacle.get_capabilities(),
)


class FileUtils:
    """
    Универсальный класс для работы с файловой системой.
    Статические методы позволяют использовать его без инициализации.
    """

    @staticmethod
    def safe_filename(name: str, replacement: str = "_") -> str:
        """Очищает имя файла от недопустимых символов."""
        return re.sub(r'[\\/*?:"<>|]', replacement, str(name))

    @staticmethod
    def ensure_dir(path: PathLike) -> Path:
        """Создает директорию, если она не существует."""
        path = Path(path)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
        return path

    @staticmethod
    async def read_text(path: PathLike, encoding: str = "utf-8") -> str:
        async with aiofiles.open(path, mode="r", encoding=encoding) as f:
            return await f.read()

    @staticmethod
    async def write_text(path: PathLike, content: str, encoding: str = "utf-8") -> None:
        async with aiofiles.open(path, mode="w", encoding=encoding) as f:
            await f.write(content)

    @staticmethod
    async def write_bytes(path: PathLike, content: bytes) -> None:
        """Асинхронная запись бинарных данных."""
        async with aiofiles.open(path, mode="wb") as f:
            await f.write(content)

    @staticmethod
    def get_file_hash(path: PathLike, algorithm: str = "md5") -> str:
        """Считает хеш файла (полезно для проверки дубликатов)."""
        hash_func = getattr(hashlib, algorithm)()
        with open(path, "rb") as f:
            # Читаем чанками, чтобы не забить память
            for chunk in iter(lambda: f.read(4096), b""):
                hash_func.update(chunk)
        return hash_func.hexdigest()

    @staticmethod
    def remove_file(path: PathLike) -> bool:
        """Безопасное удаление файла."""
        path = Path(path)
        try:
            if path.exists() and path.is_file():
                path.unlink()
                return True
        except OSError as e:
            logger.error(f"Error removing file {path}: {e}")
        return False
