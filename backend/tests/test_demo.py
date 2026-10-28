import json
from io import StringIO

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from apps.accounts.models import User
from apps.boxes.models import Box


@pytest.mark.django_db
def test_demo_is_explicit_random_and_non_destructive(tmp_path):
    output = tmp_path / "credentials.json"
    messages = StringIO()
    call_command("create_demo", namespace="test-f4", output=str(output), stdout=messages)
    assert "DEMO data created." in messages.getvalue()
    data = json.loads(output.read_text())
    assert Box.objects.count() == 12
    assert len({x["password"] for x in data["users"].values()}) == 4
    for item in data["users"].values():
        user = User.objects.get(email=item["email"])
        assert user.check_password(item["password"])
        assert user.password != item["password"]
    original = output.read_bytes()
    with pytest.raises(CommandError):
        call_command("create_demo", namespace="test-f4", output=str(output))
    assert output.read_bytes() == original
    assert User.objects.count() == 4
