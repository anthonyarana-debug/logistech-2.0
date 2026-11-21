import json
import logging
from datetime import UTC, datetime
from time import perf_counter_ns
from uuid import uuid4

STANDARD_METHODS = {"GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"}


class SafeJsonFormatter(logging.Formatter):
    """Serialize operational fields without raw messages, paths or exception values."""

    def format(self, record):
        data = {
            "timestamp": datetime.fromtimestamp(record.created, UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "event": getattr(record, "event", "log_record"),
        }
        for field in ("request_id", "status", "method", "duration_us", "exception_type"):
            if field in record.__dict__:
                data[field] = record.__dict__[field]
        if record.exc_info and record.exc_info[0]:
            data.setdefault("exception_type", record.exc_info[0].__name__)
        return json.dumps(data, separators=(",", ":"))


class RequestDiagnosticsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger("logistech.requests")

    def __call__(self, request):
        request.request_id = uuid4().hex
        started = perf_counter_ns()
        response = self.get_response(request)
        response["X-Request-ID"] = request.request_id
        if response.status_code >= 400:
            self.logger.log(
                logging.ERROR if response.status_code >= 500 else logging.WARNING,
                "Request failed",
                extra={
                    "event": "request_failed",
                    "request_id": request.request_id,
                    "status": response.status_code,
                    "method": request.method if request.method in STANDARD_METHODS else "OTHER",
                    "duration_us": (perf_counter_ns() - started) // 1000,
                },
            )
        return response
