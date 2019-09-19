import logging
import logging.config
import os

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
TELEGRAM_CHAT_IDS = [485789896]

config = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "telegram": {
            "class": "python_telegram_logger.Handler",
            "token": TELEGRAM_TOKEN,
            "chat_ids": TELEGRAM_CHAT_IDS,

        }
    },
    "loggers": {
        "tg": {
            "level": "INFO",
            "handlers": ["telegram",]
        }
    }
}

logging.config.dictConfig(config)


class ScrapeLog:

    def __init__(self):
        self.logger = logging.getLogger("tg")

    def info(self, message):
        self.logger.info(message)

    def warn(self, message):
        self.logger.warning(message)
