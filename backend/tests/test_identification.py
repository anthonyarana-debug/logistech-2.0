"""QR identifiers are stable lookup keys, never authorization credentials."""

import re
import uuid
from xml.etree import ElementTree as ET

import pytest
from rest_framework_simplejwt.tokens import AccessToken

from apps.accounts.models import User
from apps.boxes.models import Box
from apps.catalog.models import Category, Product
from apps.organizations.models import Branch, Company

pytestmark = pytest.mark.django_db


@pytest.fixture
def identified():
    company = Company.objects.create(name="Identification test")
    branch = Branch.objects.create(company=company, name="Receiving")
    category = Category.objects.create(company=company, name="Goods")
    product = Product.objects.create(company=company, category=category, sku="QR", name="Goods")
    user = User.objects.create_user("qr@example.test", company=company)
    box = Box.objects.create(
        company=company, branch=branch, product=product, created_by=user, quantity=3
    )
    return user, box


def auth(client, user):
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {AccessToken.for_user(user)}")


@pytest.mark.parametrize("role", ["SUPERADMIN", "COMPANY_ADMIN", "OPERATOR"])
def test_generate_and_resolve_qr_for_authorized_roles(client, identified, role):
    user, box = identified
    if role == "SUPERADMIN":
        user = User.objects.create_superuser("qr-root@example.test")
    elif role == "COMPANY_ADMIN":
        user.role = role
        user.save()
    auth(client, user)
    response = client.get(f"/api/v1/boxes/{box.pk}/qr/")
    assert response.status_code == 200
    data = response.json()
    assert data["payload"] == f"logistech:box:{box.qr_code}"
    assert len({str(box.pk), str(box.qr_code), box.internal_id}) == 3
    assert data["internal_id"] == box.internal_id and data["box"] == str(box.pk)
    assert ET.fromstring(data["svg"]).tag.endswith("svg")
    for code in (data["payload"], str(box.qr_code), box.internal_id.lower()):
        found = client.get("/api/v1/identification/resolve/", {"code": code})
        assert found.status_code == 200 and found.json()["id"] == str(box.pk)
    assert response["Cache-Control"] == "no-store"


def test_qr_and_printable_label_are_stable_safe_and_downloadable(client, identified):
    user, box = identified
    auth(client, user)
    first = client.get(f"/api/v1/boxes/{box.pk}/qr/").json()
    assert client.get(f"/api/v1/boxes/{box.pk}/qr/").json() == first
    result = client.get(f"/api/v1/boxes/{box.pk}/label/")
    assert result.status_code == 200 and result["Content-Type"].startswith("image/svg+xml")
    assert "attachment;" in result["Content-Disposition"]
    root = ET.fromstring(result.content)
    text = " ".join(root.itertext())
    assert box.internal_id in text
    assert str(box.qr_code) in text
    assert "password" not in result.content.decode().lower()
    assert "@example.test" not in result.content.decode()
    assert result["Cache-Control"] == "no-store"
    assert result["X-Content-Type-Options"] == "nosniff"


@pytest.mark.parametrize("label", [False, True])
def test_rendered_svg_modules_decode_with_independent_zxing_decoder(client, identified, label):
    import zxingcpp

    user, box = identified
    auth(client, user)
    if label:
        svg = client.get(f"/api/v1/boxes/{box.pk}/label/").content
        image = ET.fromstring(svg).find("{http://www.w3.org/2000/svg}svg")
    else:
        svg = client.get(f"/api/v1/boxes/{box.pk}/qr/").json()["svg"]
        image = ET.fromstring(svg)
    # Rasterize the actual square modules emitted by SvgPathImage, not a second
    # QR generation. This intentionally supports only its pinned M/H/V/H/z path.
    side = int(float(image.attrib["viewBox"].split()[2]) * 8)
    bitmap = bytearray([255]) * (side * side)
    path = image.find("{http://www.w3.org/2000/svg}path").attrib["d"]
    rectangles = re.findall(r"M([\d.]+),([\d.]+)H([\d.]+)V([\d.]+)H([\d.]+)z", path)
    assert rectangles
    for x, y, right, bottom, left in rectangles:
        assert float(left) == float(x)
        x, y, right, bottom = (round(float(v) * 8) for v in (x, y, right, bottom))
        for row in range(y, bottom):
            bitmap[row * side + x : row * side + right] = bytes(right - x)
    decoded = zxingcpp.read_barcode(memoryview(bitmap).cast("B", shape=[side, side]))
    assert decoded is not None and decoded.text == f"logistech:box:{box.qr_code}"


def test_foreign_missing_and_model_uuid_do_not_resolve(client, identified):
    _, box = identified
    foreign = Company.objects.create(name="Private QR")
    user = User.objects.create_user("foreign-qr@example.test", company=foreign)
    auth(client, user)
    for code in (str(box.qr_code), box.internal_id, str(uuid.uuid4()), str(box.pk)):
        assert client.get("/api/v1/identification/resolve/", {"code": code}).status_code == 404
    for suffix in ("qr", "label"):
        assert client.get(f"/api/v1/boxes/{box.pk}/{suffix}/").status_code == 404
    user.company = box.company
    user.save()
    assert client.get("/api/v1/identification/resolve/", {"code": str(box.pk)}).status_code == 404


@pytest.mark.parametrize(
    "params",
    [
        {},
        {"code": ""},
        {"code": "https://untrusted.example/anything"},
        {"code": "x" * 201},
        {"code": "logistech:box:bad"},
        {"code": "CJ-" + "0" * 32, "company": str(uuid.uuid4())},
    ],
)
def test_resolution_rejects_ambiguous_or_unsupported_input(client, identified, params):
    user, _ = identified
    auth(client, user)
    assert client.get("/api/v1/identification/resolve/", params).status_code == 400
    assert client.get("/api/v1/identification/resolve/?code=a&code=b").status_code == 400


def test_identification_requires_authentication_assignment_and_readonly(client, identified):
    user, box = identified
    paths = [
        "/api/v1/identification/resolve/?code=" + str(box.qr_code),
        f"/api/v1/boxes/{box.pk}/qr/",
        f"/api/v1/boxes/{box.pk}/label/",
    ]
    for path in paths:
        assert client.get(path).status_code == 401
    pending = User.objects.create_user("pending-qr@example.test")
    auth(client, pending)
    for path in paths:
        assert client.get(path).status_code == 403
    auth(client, user)
    for path in paths:
        assert client.post(path, {}, format="json").status_code == 405
    user.company.status = "INACTIVE"
    user.company.save()
    assert client.get(paths[0]).status_code == 403


def test_identification_uses_unchanged_private_rate_limit(client, identified):
    user, box = identified
    auth(client, user)
    for _ in range(120):
        assert client.get(f"/api/v1/boxes/{box.pk}/qr/").status_code == 200
    limited = client.get("/api/v1/identification/resolve/", {"code": str(box.qr_code)})
    assert limited.status_code == 429 and int(limited["Retry-After"]) > 0


def test_new_metadata_uses_english_presentation_labels(client, identified):
    user, _ = identified
    auth(client, user)
    response = client.options("/api/v1/receipts/")
    assert response.status_code == 200
    fields = response.json()["actions"]["POST"]
    assert fields["company"]["label"] == "Company"
    assert fields["branch"]["label"] == "Branch"
    assert "Registrada" not in response.content.decode()
