"""Translate generated Admin labels only; never translate cell values or user data."""

import re

from django import template
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

from apps.core.labels import FIELD_LABELS, LEGACY_LABELS

register = template.Library()
LABELS = {
    **LEGACY_LABELS,
    "correo electrónico": "Email address",
    "rol": "Role",
    "nombre": "Name",
    "dirección": "Address",
    "descripción": "Description",
    "frágil": "Fragile",
    "perecedera": "Perishable",
    "cantidad": "Quantity",
    "peso kg": "Weight (kg)",
}
LABELS.update({key: value for key, value in FIELD_LABELS.items()})


@register.filter
def english_label(value):
    text = str(value)
    return LABELS.get(text.lower(), text)


@register.filter
def english_label_tag(value):
    # The source label is escaped unless it was already a trusted Django label tag.
    escaped = str(conditional_escape(value))
    translated = re.sub(
        r">([^<>]+):</label>",
        lambda match: ">" + english_label(match[1]).capitalize() + ":</label>",
        escaped,
    )
    return mark_safe(translated)  # Generated labels only; original text remains escaped.
