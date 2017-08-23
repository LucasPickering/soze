import logging
import logging.config
from flask import Flask

logging.config.dictConfig({
    'version': 1,
    'formatters': {
        'f': {
            'format': '{asctime} - {levelname} - {message}',
            'datefmt': '%Y-%m-%d %H:%M:%S',
            'style': '{',
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'f',
        },
        'file': {
            'class': 'logging.FileHandler',
            'formatter': 'f',
            'filename': 'server.log',
            'mode': 'w',
        },
    },
    'loggers': {
        __name__: {
            'handlers': ['console', 'file'],
            'level': 'INFO',
        },
    },
})

app = Flask(__name__)
logger = logging.getLogger(__name__)
