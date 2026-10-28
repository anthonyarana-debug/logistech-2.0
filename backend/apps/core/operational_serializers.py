from collections.abc import Mapping

from rest_framework import serializers

from .labels import CHOICE_LABELS, FIELD_LABELS
from .operations_messages import text


class OperationalSerializer(serializers.ModelSerializer):
    """Deny unknown and read-only fields, including hidden Django privileges."""

    def get_fields(self):
        fields = super().get_fields()
        for name, field in fields.items():
            field.label = FIELD_LABELS.get(name, name.replace("_", " ").capitalize())
            if isinstance(field, serializers.ChoiceField):
                field.choices = [
                    (v, CHOICE_LABELS.get(v, label)) for v, label in field.choices.items()
                ]
        return fields

    def to_internal_value(self, data):
        if not isinstance(data, Mapping) or any(
            key not in self.fields or self.fields[key].read_only for key in data
        ):
            raise serializers.ValidationError({"campos": text("invalid_object")})
        return super().to_internal_value(data)
