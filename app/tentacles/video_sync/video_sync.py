# app/tentacles/video_sync.py (Офер Потребителя/Разработчика)
from typing import Any

from pybreaker import CircuitBreaker  # Используем библиотеку Circuit Breaker

from app.brain import CommandContext, CommandDispatchTentacle, OctaResponse, TentacleMetadata

from .video_sync_model import VideoPayload

# Инициализируем выключатель для этого щупальца
# failure_threshold=5: Сломается после 5 сбоев
# reset_timeout=30: Попробует снова через 30 секунд
video_breaker = CircuitBreaker(fail_max=5, reset_timeout=30)


class VideoSyncStandinTentacle(CommandDispatchTentacle):
    """
    Standin-реализация логики скачивания видео (для работы в Теле).
    """

    # 1. ПЕРЕНОС ДИСПЕТЧЕРА НА УРОВЕНЬ КЛАССА
    # Обратите внимание: сохраняем только имя метода
    _COMMAND_HANDLERS = {
        "DOWNLOAD_VIDEO": "_handle_download_video",
        "CHECK_VIDEO_HEALTH": "_handle_check_video_health",
        # ... и так далее
    }

    async def _handle_download_video(self, context: CommandContext) -> OctaResponse[VideoPayload]:
        """Логика обработки команды DOWNLOAD_VIDEO."""
        print(f"  [STANDIN: VideoSync]: Загружаю видео по URL: {context.params.get('url')}...")
        # ... Здесь 200 строк реальной логики скачивания ...
        payload = VideoPayload(filename="video.mp4", size_mb=150.0, duration=30, path="d:/ghd")
        return OctaResponse.ok(data=payload)

    async def _handle_check_video_health(self, context: CommandContext) -> OctaResponse[Any]:
        """Логика проверки здоровья видео."""
        print(
            f"  [STANDIN: VideoSync]: Проверяю здоровье видео ID: {context.params.get('video_id')}..."
        )
        # ... Здесь 200 строк логики проверки ...
        return OctaResponse.ok(data={"status": "healthy"})

    async def get_health(self) -> float:
        return 1.0


# --- РЕГИСТРАЦИЯ В ГЕНОМЕ В РАНТАЙМЕ ---
# --- МЕТАДАННЫЕ (ОФЕР) ---
TENTACLE_METADATA = TentacleMetadata(
    tentacle_id="VIDEO_DOWNLOADER",
    contract_interface=CommandDispatchTentacle,
    internal_implementation=VideoSyncStandinTentacle,
    external_image_tag="octamillia/video_sync:v1.0",
    handles_commands=VideoSyncStandinTentacle.get_capabilities(),
)
# ВАЖНО: Мозг или процесс инициализации системы загружает этот файл
# и добавляет метаданные в глобальный WAI_REGISTRY!
