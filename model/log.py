import logging
from logging.config import dictConfig


def get_log():
    logging_config = dict(
        version=1,
        formatters={
            "f": {"format": "%(asctime)s %(name)-12s %(levelname)-8s %(message)s"}
        },
        handlers={
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "f",
                "level": logging.DEBUG,
                "filename": "app.log",
                "maxBytes": 1048576,  # 1 MB
                "backupCount": 3,  # Manter até 3 arquivos de backup
            },
            "stream": {
                "class": "logging.StreamHandler",
                "formatter": "f",
                "level": logging.DEBUG,
            },
        },
        root={
            "handlers": ["file", "stream"],
            "level": logging.DEBUG,
        },
    )

    dictConfig(logging_config)

    return logging.getLogger()
