# app/body/body.py
from app.body.interfaces import IMessageBus


class Body:
    def assemble_organism(self, bus_implementation: IMessageBus):
        for TentacleClass in self.tentacle_templates:  # Обнаружение
            # 1. Создание инстанса (Инжекция)
            tentacle = TentacleClass(message_bus=bus_implementation)

            # 2. Автоматическая подписка
            handlers = tentacle.get_event_handlers()
            for topic, method_name in handlers.items():
                handler_method = getattr(tentacle, method_name)
                # Мозг подписывает метод Щупальца на транспорт
                bus_implementation.subscribe(topic, handler_method)

        # Сохранить все собранные инстансы в каталог для route_command
