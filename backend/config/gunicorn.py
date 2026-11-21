bind = "0.0.0.0:8000"
workers = 2
threads = 2
forwarded_allow_ips = "*"
accesslog = "-"
errorlog = "-"
access_log_format = (
    '{"status":%(s)s,"method":"%(m)s","duration_us":%(D)s,'
    '"request_id":"%({x-request-id}o)s"}'
)

logconfig_dict = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "safe_json": {"()": "apps.core.observability.SafeJsonFormatter"},
    },
    "handlers": {
        "error_console": {
            "class": "logging.StreamHandler",
            "formatter": "safe_json",
            "stream": "ext://sys.stderr",
        },
        "access_console": {
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
    },
    "root": {"handlers": ["error_console"], "level": "WARNING"},
    "loggers": {
        "gunicorn.error": {"handlers": ["error_console"], "level": "INFO", "propagate": False},
        "gunicorn.access": {"handlers": ["access_console"], "level": "INFO", "propagate": False},
    },
}
