import logging
import logging.config

logging.config.dictConfig(
    {
        "version": 1,
        "formatters": {
            "f": {
                "format": "{asctime} [{threadName} {levelname}] {message}",
                "datefmt": "%Y-%m-%d %H:%M:%S",
                "style": "{",
            }
        },
        "handlers": {
            "console": {"class": "logging.StreamHandler", "formatter": "f"}
        },
        "loggers": {__name__: {"handlers": ["console"], "level": "INFO"}},
    }
)

logger = logging.getLogger(__name__)
