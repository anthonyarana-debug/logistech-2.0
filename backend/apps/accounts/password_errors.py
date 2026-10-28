"""Render password errors with English presentation labels, without changing rules."""

from django.core.exceptions import ValidationError
from rest_framework.exceptions import ErrorDetail


def password_error_details(error, user):
    labels = {
        "email": "email address",
        "first_name": "first name",
        "last_name": "last name",
        "username": "username",
    }
    metadata_labels = {
        str(field.verbose_name): labels[field.name]
        for field in user._meta.fields
        if field.name in labels
    }
    details = []
    for item in error.error_list:
        # Copy params; retain Django's template/code and all non-label values.
        # Only this validator's model metadata parameter is presentation text.
        params = dict(item.params or {})
        if item.code == "password_too_similar" and "verbose_name" in params:
            original = str(params["verbose_name"])
            if original in metadata_labels:
                params["verbose_name"] = metadata_labels[original]
        rendered = ValidationError(item.message, code=item.code, params=params)
        details.extend(ErrorDetail(value, code=item.code) for value in rendered.messages)
    return details
