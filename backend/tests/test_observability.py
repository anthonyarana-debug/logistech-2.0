import json
import logging
from uuid import UUID

from apps.core.observability import SafeJsonFormatter


def test_failure_response_and_log_share_server_generated_id(client, caplog):
    with caplog.at_level(logging.WARNING, logger="logistech.requests"):
        response = client.get("/api/v1/missing/?private=hidden", HTTP_X_REQUEST_ID="untrusted")

    request_id = response["X-Request-ID"]
    assert UUID(request_id).version == 4
    assert response.status_code == 404
    event = next(record for record in caplog.records if record.name == "logistech.requests")
    payload = json.loads(SafeJsonFormatter().format(event))
    assert payload["request_id"] == request_id
    assert payload["status"] == 404
    assert payload["method"] == "GET"
    assert payload["duration_us"] >= 0
    assert "hidden" not in str(payload)
    assert "untrusted" not in str(payload)


def test_formatter_omits_raw_message_and_exception_value():
    try:
        raise ValueError("private-token")
    except ValueError:
        import sys

        record = logging.LogRecord(
            "test", logging.ERROR, "", 1, "raw-secret", (), sys.exc_info(),
        )

    output = SafeJsonFormatter().format(record)
    assert json.loads(output)["exception_type"] == "ValueError"
    assert "raw-secret" not in output
    assert "private-token" not in output
