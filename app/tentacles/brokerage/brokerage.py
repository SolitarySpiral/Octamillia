# app/tentacles/brokerage/tentacle.py (Пример)
from app.body.blood import OctaEvent
from app.body.interfaces import IMessageBus
from app.brain import CommandDispatchTentacle, TentacleMetadata


class BrokerageTentacle(CommandDispatchTentacle):
    # 1. ПЕРЕНОС ДИСПЕТЧЕРА НА УРОВЕНЬ КЛАССА
    _COMMAND_HANDLERS = {}

    _EVENT_HANDLERS = {
        "ORDER_TOPIC": "_handle_incoming_order",
        # "PRICE_UPDATE": "_handle_market_data",
    }

    # Инжектируем IMessageBus
    def __init__(self, message_bus: IMessageBus, logger, tentacle_id: str, **kwargs):
        # Передаем все аргументы в базовый класс
        super().__init__(message_bus=message_bus, logger=logger, tentacle_id=tentacle_id, **kwargs)
        self.message_bus = message_bus
        self.logger = logger

    async def _handle_incoming_order(self, event: OctaEvent):
        """Обрабатывает асинхронное сообщение, пришедшее из "вены"."""
        self.logger.info(f"Получен новый ордер: {event.payload}")
        # ... здесь выполняется бизнес-логика (например, сохранить в БД) ...

        # Может отправить ответное сообщение (артерия)
        response_event = OctaEvent(
            event="ORDER_RECEIVED", payload={"order_id": event.payload["id"]}
        )
        await self.message_bus.publish("INTERNAL_FEEDBACK", response_event)

    async def get_health(self) -> float:
        return 1.0


TENTACLE_METADATA = TentacleMetadata(
    tentacle_id="Brokerage",
    contract_interface=CommandDispatchTentacle,
    internal_implementation=BrokerageTentacle,
    external_image_tag="octamillia/brokerage:v1.0",
    handles_commands=BrokerageTentacle.get_capabilities(),
)
