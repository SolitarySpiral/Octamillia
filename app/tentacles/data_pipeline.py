# app/tentacles/data_pipeline.py
from app.brain import TentacleMetadata
from app.suckers.outputs.logger import LoggerSucker
from app.suckers.transformers.multiplier import MultiplierSucker
from app.suckers.validators.int_validator import IntValidatorSucker

from .pipeline_tentacle import PipelineTentacle


class DataPipelineTentacle(PipelineTentacle):
    """Конкретная тентакля с готовым набором присосок"""

    def __init__(self, **kwargs):
        # Определяем порядок присосок в конвейере
        suckers = [
            IntValidatorSucker(),  # 1. Валидация
            MultiplierSucker(factor=3),  # 2. Преобразование
            LoggerSucker(),  # 3. Логирование
            MultiplierSucker(factor=2),  # 4. Еще одно преобразование
            LoggerSucker(),  # 5. Финальное логирование
        ]
        super().__init__(suckers=suckers, **kwargs)


# --- МЕТАДАННЫЕ ДЛЯ WAI ---
TENTACLE_METADATA = TentacleMetadata(
    tentacle_id="DATA_PIPELINE",
    contract_interface=PipelineTentacle,
    internal_implementation=DataPipelineTentacle,
    external_image_tag="octamillia/data_pipeline:v1.0",
    handles_commands=DataPipelineTentacle.get_capabilities(),
)
