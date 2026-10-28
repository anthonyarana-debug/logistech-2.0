"""Atomic reception and bounded, append-only box history."""

from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework.exceptions import NotFound, PermissionDenied

from apps.catalog.models import Category, Product
from apps.core.api import Conflict, is_global
from apps.organizations.models import Branch, Company

from .models import Box, BoxEvent, Receipt


def record_event(box, actor, event_type, data=None):
    snapshot = {
        "product": str(box.product_id),
        "branch": str(box.branch_id),
        "quantity": box.quantity,
        "weight_kg": str(box.weight_kg) if box.weight_kg else None,
        "priority": box.priority,
        "status": box.status,
    }
    snapshot.update(data or {})
    return BoxEvent.objects.create(
        box=box.pk,
        internal_id=box.internal_id,
        company_id=box.company_id,
        branch_id=box.branch_id,
        actor=actor,
        event_type=event_type,
        outcome=box.status,
        data=snapshot,
    )


def validate_actor(actor):
    if not actor.is_active or not (
        is_global(actor)
        or (actor.role in {actor.Role.OPERATOR, actor.Role.COMPANY_ADMIN} and actor.company_id)
    ):
        raise PermissionDenied("An assigned active account is required.")


@transaction.atomic
def receive_box(*, actor, box_id, branch_id, result, reason, key, source):
    """Caller locks actor first. Match CRUD lock order: box, company, references.

    Actor locking serializes same-user keys; box locking serializes different
    operators finalizing the same box. DB uniqueness is the final backstop.
    """
    actor = get_user_model().objects.select_for_update().filter(pk=actor.pk).first()
    if actor is None:
        raise PermissionDenied("The account is unavailable.")
    validate_actor(actor)
    boxes = Box.objects.select_for_update()
    if not is_global(actor):
        boxes = boxes.filter(company_id=actor.company_id)
    box = boxes.filter(pk=box_id).first()
    if box is None:
        raise NotFound("Box is unavailable.")
    company = Company.objects.select_for_update().get(pk=box.company_id)
    if company.status != Company.Status.ACTIVE:
        raise Conflict("The company must be active to receive boxes.")
    existing = Receipt.objects.filter(company=company, actor=actor, idempotency_key=key).first()
    if existing:
        if (
            existing.box_id,
            existing.branch_id,
            existing.result,
            existing.reason,
            existing.source,
        ) != (box.pk, branch_id, result, reason, source):
            raise Conflict("The idempotency key was already used for another request.")
        return existing, True
    if box.branch_id != branch_id:
        raise Conflict("The receiving branch must match the box branch.")
    if box.status != Box.Status.REGISTERED:
        raise Conflict("Only a registered box can be received or rejected once.")
    product = Product.objects.select_for_update().filter(pk=box.product_id).first()
    branch = Branch.objects.select_for_update().filter(pk=box.branch_id).first()
    category = (
        Category.objects.select_for_update().filter(pk=product.category_id).first()
        if product
        else None
    )
    if (
        not product
        or not branch
        or not category
        or any(item.company_id != company.pk for item in (product, branch, category))
        or product.status != Company.Status.ACTIVE
        or branch.status != Company.Status.ACTIVE
    ):
        raise Conflict("References must be active and belong to the box company.")
    receipt = Receipt.objects.create(
        box=box,
        internal_id=box.internal_id,
        company=company,
        branch=branch,
        actor=actor,
        result=result,
        reason=reason,
        idempotency_key=key,
        source=source,
    )
    box.status = result
    box.save(update_fields=["status"])
    record_event(
        box,
        actor,
        BoxEvent.EventType.RECEIPT_RECORDED,
        {
            "receipt": str(receipt.pk),
            "result": result,
            "reason": reason,
            "source": source,
        },
    )
    return receipt, False
