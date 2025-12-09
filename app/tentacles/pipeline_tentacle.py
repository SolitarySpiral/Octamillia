# app/tentacles/pipeline_tentacle.py
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from app.brain import CommandContext, CommandDispatchTentacle, OctaResponse
from app.suckers.base import ISucker, SuckerContext


class PipelineTentacle(CommandDispatchTentacle):
    """Тентакля-конвейер, которая использует присоски"""

    # ДИСПЕТЧЕР КОМАНД (наследуется от CommandDispatchTentacle)
    _COMMAND_HANDLERS = {"PROCESS_PIPELINE": "_process_pipeline"}

    # ОБРАБОТЧИКИ СОБЫТИЙ (для подписки на шину)
    _EVENT_HANDLERS = {"PIPELINE_COMPLETE": "_handle_pipeline_complete"}

    def __init__(self, suckers: List[ISucker] = None, **kwargs):
        super().__init__(**kwargs)
        self.suckers = suckers or []  # Упорядоченный список присосок

    async def _process_pipeline(self, context: CommandContext) -> OctaResponse[Dict[str, Any]]:
        """Запускает конвейер присосок"""

        print(f"\n[PipelineTentacle] Запуск конвейера с {len(self.suckers)} присосками")

        # 1. Создаем начальный контекст
        sucker_context = SuckerContext(
            data=context.params.get("data", {}),
            metadata={
                "command": context.command_name,
                "correlation_id": context.correlation_id,
                "user_id": context.user_id,
                "pipeline_id": f"pipe_{context.correlation_id}",
                "suckers_count": len(self.suckers),
            },
        )

        # 2. Прогоняем через все присоски
        for i, sucker in enumerate(self.suckers):
            try:
                sucker_name = sucker.__class__.__name__
                print(f"  [{i + 1}/{len(self.suckers)}] Присоска: {sucker_name}")

                # Обработка
                sucker_context = await sucker.process(sucker_context)

                # Проверка статуса
                if sucker_context.status == "ERROR":
                    print(f"    ✗ Ошибка в присоске {sucker_name}")

                    # Записываем ошибку в "жопу" (логируем пока что)
                    await self._log_to_ass(sucker_context, failed_at=sucker_name)

                    return OctaResponse.fail(
                        f"Ошибка в присоске {sucker_name}: {sucker_context.data.get('error', 'Неизвестная ошибка')}"
                    )

                elif sucker_context.status == "ROLLBACK":
                    print(f"    ↺ Откат от присоски {sucker_name}")
                    # Логика отката (пока просто останавливаемся)
                    return OctaResponse.fail("Конвейер откатил изменения")

                print("    ✓ Успех")

            except Exception as e:
                print(f"    💥 Сбой в присоске {sucker.__class__.__name__}: {e}")
                await self._log_to_ass(sucker_context, exception=str(e))
                return OctaResponse.fail(f"Сбой в присоске {i + 1}: {str(e)}")

        # 3. Успешное завершение
        sucker_context.status = "SUCCESS"
        print("[PipelineTentacle] Конвейер завершен успешно!")

        # 4. Записываем в "пред-жопие" (буфер для финальной коммитации)
        await self._commit_to_pre_ass(sucker_context)

        # 5. Отправляем событие о завершении
        try:
            if hasattr(self, "message_bus") and self.message_bus:
                from app.body.blood import OctaEvent

                complete_event = OctaEvent(
                    event="PIPELINE_COMPLETE", payload=sucker_context.model_dump()
                )
                await self.message_bus.publish("PIPELINE_COMPLETE", complete_event)
        except Exception as e:
            print(f"[PipelineTentacle] Не удалось отправить событие: {e}")

        return OctaResponse.ok(
            data={
                "result": sucker_context.data,
                "metadata": sucker_context.metadata,
                "status": "COMPLETED",
            },
            command_name=context.command_name,
            correlation_id=context.correlation_id,
        )

    async def _handle_pipeline_complete(self, event):
        """Обработчик события завершения конвейера"""
        print(f"[PipelineTentacle] Получено событие завершения: {event.event}")
        # Можно сделать что-то по завершению всех конвейеров

    async def _commit_to_pre_ass(self, context: SuckerContext):
        """Буферизация в пред-жопии (заглушка)"""
        print(f"[PipelineTentacle] Финализация в пред-жопии: {context.metadata['pipeline_id']}")
        # Здесь будет логика буферизации перед записью в основное хранилище
        # Например: запись в Redis, файл или очередь сообщений

    async def _log_to_ass(self, context: SuckerContext, **kwargs):
        """Логирование в 'жопу' (реализация через файл)"""
        error_data = {
            "timestamp": datetime.now().isoformat(),
            "pipeline_id": context.metadata.get("pipeline_id"),
            "error": context.data.get("error"),
            "metadata": context.metadata,
            **kwargs,
        }

        # Простая реализация - запись в JSON файл
        log_file = Path("./storage/ass_errors.json")
        log_file.parent.mkdir(exist_ok=True)

        existing = []
        if log_file.exists():
            existing = json.loads(log_file.read_text())

        existing.append(error_data)
        log_file.write_text(json.dumps(existing, indent=2, ensure_ascii=False))

        print(f"[PipelineTentacle] Ошибка записана в жопу: {error_data['error']}")

    async def get_health(self) -> float:
        """Проверка здоровья конвейера"""
        return 1.0  # Все присоски здоровы
