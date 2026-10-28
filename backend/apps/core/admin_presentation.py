"""English Admin presentation without changing model/migration metadata."""

import re
from copy import copy

from django.contrib.admin.widgets import RelatedFieldWidgetWrapper
from django.utils.safestring import SafeData, mark_safe

from .labels import CHOICE_LABELS, FIELD_LABELS, LEGACY_LABELS, MODEL_LABELS
from .messages import domain_message


def presentation_options(options):
    """Copy labels for a template; never mutate the registered model's Options."""
    result = copy(options)
    labels = MODEL_LABELS.get(options.model_name)
    if labels:
        result.verbose_name, result.verbose_name_plural = labels
    return result


def object_tree(items):
    """Translate only generated type prefixes; preserve every user-supplied suffix."""
    result = []
    for item in items:
        if isinstance(item, list):
            result.append(object_tree(item))
            continue
        for old, new in LEGACY_LABELS.items():
            prefix = f"{old.capitalize()}: "
            if isinstance(item, str) and item.startswith(prefix):
                item = f"{new.capitalize()}: " + item[len(prefix) :]
                break
        result.append(item)
    return result


class EnglishRelatedWidgetWrapper(RelatedFieldWidgetWrapper):
    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context["model"] = LEGACY_LABELS.get(context["model"], context["model"])
        return context


class EnglishValidationMixin:
    def _update_errors(self, errors):
        groups = (
            errors.error_dict.values() if hasattr(errors, "error_dict") else [errors.error_list]
        )
        for group in groups:
            for error in group:
                error.message = domain_message(error.message)
                if error.params and "model_name" in error.params:
                    value = error.params["model_name"]
                    error.params["model_name"] = LEGACY_LABELS.get(str(value), value)
                if error.params and "field_label" in error.params:
                    from .templatetags.english_presentation import english_label

                    error.params["field_label"] = english_label(error.params["field_label"])
        return super()._update_errors(errors)


class EnglishAdminMixin:
    def message_user(self, request, message, *args, **kwargs):
        # Only Django-generated type labels change; object names and HTML remain intact.
        text = str(message)
        for old, new in LEGACY_LABELS.items():
            prefix = f"The {old} "
            if text.startswith(prefix):
                text = f"The {new} " + text[len(prefix) :]
                break
            text = re.sub(
                rf"^Successfully deleted (\d+) {old}\.$",
                rf"Successfully deleted \1 {new}.",
                text,
            )
        if isinstance(message, SafeData):
            text = mark_safe(text)
        return super().message_user(request, text, *args, **kwargs)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        localized = type("English" + form.__name__, (EnglishValidationMixin, form), {})
        for name, field in localized.base_fields.items():
            field.label = FIELD_LABELS.get(name, field.label)
            widget = field.widget
            if isinstance(widget, RelatedFieldWidgetWrapper):
                field.widget = EnglishRelatedWidgetWrapper(
                    widget.widget,
                    widget.rel,
                    widget.admin_site,
                    can_add_related=widget.can_add_related,
                    can_change_related=widget.can_change_related,
                    can_delete_related=widget.can_delete_related,
                    can_view_related=widget.can_view_related,
                )
        return localized

    def formfield_for_choice_field(self, db_field, request, **kwargs):
        field = super().formfield_for_choice_field(db_field, request, **kwargs)
        if field:
            field.choices = [
                (value, CHOICE_LABELS.get(value, label)) for value, label in field.choices
            ]
        return field

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context)
        if getattr(response, "context_data", None):
            options = presentation_options(self.opts)
            response.context_data["opts"] = options
            response.context_data["cl"].opts = options
            response.context_data["title"] = f"Select {options.verbose_name} to change"
        return response

    def render_change_form(self, request, context, add=False, change=False, form_url="", obj=None):
        response = super().render_change_form(request, context, add, change, form_url, obj)
        options = presentation_options(self.opts)
        response.context_data["opts"] = options
        response.context_data["title"] = f"{'Add' if add else 'Change'} {options.verbose_name}"
        return response

    def history_view(self, request, object_id, extra_context=None):
        response = super().history_view(request, object_id, extra_context)
        if getattr(response, "context_data", None):
            response.context_data["opts"] = presentation_options(self.opts)
        return response

    def delete_view(self, request, object_id, extra_context=None):
        response = super().delete_view(request, object_id, extra_context)
        if getattr(response, "context_data", None):
            options = presentation_options(self.opts)
            response.context_data["opts"] = options
            response.context_data["object_name"] = options.verbose_name
            response.context_data["title"] = (
                f"Cannot delete {options.verbose_name}"
                if response.context_data.get("protected")
                else "Are you sure?"
            )
        return response

    def get_deleted_objects(self, objs, request):
        deleted, counts, permissions, protected = super().get_deleted_objects(objs, request)
        counts = {LEGACY_LABELS.get(name, name): count for name, count in counts.items()}
        return object_tree(deleted), counts, permissions, object_tree(protected)
