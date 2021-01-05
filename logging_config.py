import os
import logging.config


def init_logger():
    os.makedirs('logs', exist_ok=True)
    logging_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
            },
        },
        'handlers': {
            'default_handler_warn_error': {
                'class': 'logging.FileHandler',
                'level': 'WARN',
                'formatter': 'standard',
                'filename': os.path.join('logs', 'application.log'),
                'encoding': 'utf8'
            },
            'default_handler_debug': {
                'class': 'logging.FileHandler',
                'level': 'DEBUG',
                'formatter': 'standard',
                'filename': os.path.join('logs', 'application.debug.log'),
                'encoding': 'utf8'
            },
            'default_stdout': {
                'level': 'INFO',
                'formatter': 'standard',
                'class': 'logging.StreamHandler',
                'stream': 'ext://sys.stdout',  # Default is stderr
            },
        },
        'loggers': {
            '': {
                'handlers': ['default_handler_warn_error', 'default_handler_debug', 'default_stdout'],
                'level': 'DEBUG',
                'propagate': False
            }
        }
    }
    logging.config.dictConfig(logging_config)