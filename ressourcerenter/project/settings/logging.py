LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "gunicorn": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["gunicorn"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["gunicorn"],
            "level": "INFO",
            "propagate": False,
        },
    },
}
