"""Regressions for the DRF 3.18.2 security fixes retained in 3.18.3.

Upstream: https://www.django-rest-framework.org/community/release-notes/#3182
GHSA-3547-9m27-7rxg / CVE-2026-114136: non-text JSON charsets.
GHSA-33wh-fxxf-88vv / CVE-2026-114138: unbounded Accept negotiation.
GHSA-xw6w-gcfp-cf8m / CVE-2026-114137 concerns DRF TokenProxy,
which this project does not install or use (it uses SimpleJWT). Existing
auth tests exercise refresh-token rotation, replay rejection and logout.
The dependency is upgraded to remove all three vulnerable implementations.
"""

import codecs
from io import BytesIO
from unittest.mock import Mock

import pytest
from rest_framework.exceptions import ParseError
from rest_framework.negotiation import DefaultContentNegotiation
from rest_framework.parsers import JSONParser
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory


@pytest.mark.parametrize("encoding", ["bz2_codec", "zlib_codec", "base64_codec"])
def test_json_refuses_byte_transform_codecs_before_reading_body(encoding):
    stream = BytesIO(codecs.encode(b'{"email":"example@example.invalid"}', encoding))
    stream.read = Mock(wraps=stream.read)
    with pytest.raises(ParseError):
        JSONParser().parse(stream, parser_context={"encoding": encoding})
    stream.read.assert_not_called()


def test_json_still_accepts_utf8_text():
    payload = '{"name":"Logística"}'
    assert JSONParser().parse(
        BytesIO(payload.encode("utf-8")), parser_context={"encoding": "utf-8"}
    ) == {"name": "Logística"}


def test_accept_negotiation_bounds_attacker_controlled_token_count():
    header = ",".join(f"application/x-type-{index}" for index in range(1000))
    request = Request(APIRequestFactory().get("/api/v1/auth/csrf/", HTTP_ACCEPT=header))
    tokens = DefaultContentNegotiation().get_accept_list(request)
    assert len(tokens) <= 64
    assert all(len(token) <= 256 for token in tokens)


def test_accept_negotiation_skips_large_token_and_keeps_valid_json():
    header = 'application/example; padding="' + "x" * 300 + '", application/json'
    request = Request(APIRequestFactory().get("/api/v1/auth/csrf/", HTTP_ACCEPT=header))
    assert DefaultContentNegotiation().get_accept_list(request) == ["application/json"]


def test_login_api_rejects_compressed_json_charset_with_existing_error_schema(client):
    csrf_response = client.get("/api/v1/auth/csrf/")
    client.credentials(HTTP_X_CSRFTOKEN=csrf_response.json()["csrfToken"])
    response = client.post(
        "/api/v1/auth/login/",
        codecs.encode(b'{"email":"example@example.invalid"}', "bz2_codec"),
        content_type="application/json; charset=bz2_codec",
    )
    assert response.status_code == 400
    assert set(response.json()) == {"errores"}


@pytest.mark.parametrize(
    ("header", "expected_status"),
    [
        ("application/json," + ",".join(f"application/x-{index}" for index in range(1000)), 200),
        ('application/example; padding="' + "x" * 9000 + '"', 406),
    ],
)
def test_csrf_api_handles_oversized_accept_headers_safely(client, header, expected_status):
    response = client.get("/api/v1/auth/csrf/", HTTP_ACCEPT=header)
    assert response.status_code == expected_status
    assert set(response.json()) == ({"csrfToken"} if expected_status == 200 else {"errores"})
