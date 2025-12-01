import logging


def setup_logger():
    # Ваша логика настройки логгера
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] - %(name)s-%(filename)s:%(funcName)s():"
        "%(lineno)d - %(levelname)s - %(message)s",
    )
    logger = logging.getLogger("app")
    # ... добавьте обработчики и форматирование ...
    return logger


# Создайте экземпляр логгера, который будут импортировать другие модули
logger = setup_logger()
