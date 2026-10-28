import re
import uuid

from django.db import OperationalError, transaction
from django.db.models import F
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from apps.catalog.models import Product
from apps.core.api import Conflict, ResourcePermission, TenantViewSet, is_global
from apps.core.messages import message
from apps.organizations.models import Branch, Company

from .models import Box, BoxEvent, Receipt
from .reception import receive_box, record_event
from .serializers import (
    BoxEventSerializer,
    BoxSerializer,
    ReceiptRequestSerializer,
    ReceiptSerializer,
)


class ReceptionConflictMixin:
    """Report rolled-back PostgreSQL transaction conflicts as safe retries."""

    def handle_exception(self, exc):
        if isinstance(exc, OperationalError):
            cause = exc.__cause__
            if getattr(cause, "sqlstate", None) in {"40P01", "40001"}:
                exc = Conflict(
                    "A concurrent update conflicted with this operation. "
                    "Retry the request using the same idempotency key."
                )
        return super().handle_exception(exc)


class BoxViewSet(ReceptionConflictMixin, TenantViewSet):
    queryset = Box.objects.filter(
        product__company_id=F("company_id"),
        branch__company_id=F("company_id"),
        product__category__company_id=F("company_id"),
    ).select_related("company", "product__category", "branch", "created_by")
    serializer_class = BoxSerializer
    operator_write = True
    uuid_filters = {
        "company": "company_id",
        "product": "product_id",
        "branch": "branch_id",
        "category": "product__category_id",
        "qr_code": "qr_code",
    }
    choice_filters = {"status": Box.Status.values, "priority": Box.Priority.values}
    extra_filters = ("internal_id",)
    search_fields = ("internal_id", "product__name", "product__sku")

    def filter_extra(self, queryset, params):
        if "internal_id" in params:
            value = params["internal_id"].upper()
            if not re.fullmatch(r"CJ-[A-F0-9]{32}", value):
                raise ValidationError({"internal_id": message("invalid_internal_identifier")})
            queryset = queryset.filter(internal_id=value)
        return queryset

    def lock_references(self, serializer, company):
        """Lock and validate active references against the selected company."""
        for key, model in (("product", Product), ("branch", Branch)):
            related = serializer.validated_data.get(key) or getattr(serializer.instance, key, None)
            related = model.objects.select_for_update().filter(pk=related.pk).first()
            if related is None:
                raise Conflict(message("a_reference_is_no_longer_available"))
            if related.company_id != company.pk or related.status != Company.Status.ACTIVE:
                raise Conflict(message("references_must_be_active_and_belong_to_the_company"))
            if key == "product":
                category = related.category
                if category.company_id != company.pk:
                    raise Conflict(message("references_must_belong_to_the_company"))
            serializer.validated_data[key] = related

    def perform_create(self, serializer):
        company = self.lock_company(serializer.validated_data["company"])
        self.lock_references(serializer, company)
        serializer.save(company=company, created_by=self.request.user)
        record_event(serializer.instance, self.request.user, BoxEvent.EventType.BOX_CREATED)

    def perform_update(self, serializer):
        changed_fields = {
            key
            for key, value in serializer.validated_data.items()
            if getattr(serializer.instance, key) != value
        }
        company = self.lock_company(serializer.instance.company)
        self.lock_references(serializer, company)
        terminal = serializer.validated_data.get("status")
        if (
            terminal in {Box.Status.RECEIVED, Box.Status.REJECTED}
            and serializer.instance.status == Box.Status.REGISTERED
        ):
            serializer.validated_data.pop("status")
            if changed_fields - {"status"}:
                serializer.save(company=company)
                record_event(serializer.instance, self.request.user, BoxEvent.EventType.BOX_UPDATED)
            receipt, _ = receive_box(
                actor=self.request.user,
                box_id=serializer.instance.pk,
                branch_id=serializer.instance.branch_id,
                result=terminal,
                reason=Receipt.Reason.OTHER if terminal == Box.Status.REJECTED else "",
                key=uuid.uuid4(),
                source=Receipt.Source.BOX_STATUS_UPDATE,
            )
            serializer.instance.status = receipt.result
        else:
            serializer.save(company=company)
            if changed_fields:
                record_event(serializer.instance, self.request.user, BoxEvent.EventType.BOX_UPDATED)

    def perform_destroy(self, instance):
        if instance.status != Box.Status.REGISTERED:
            raise Conflict(
                message("only_registered_boxes_without_reception_or_rejection_can_be_deleted")
            )
        self.lock_company(instance.company)
        record_event(instance, self.request.user, BoxEvent.EventType.BOX_DELETED)
        instance.delete()


class ReceptionPermission(ResourcePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated or not user.is_active:
            return False
        return is_global(user) or (
            user.role in {user.Role.OPERATOR, user.Role.COMPANY_ADMIN}
            and user.company_id is not None
            and user.company.status == Company.Status.ACTIVE
        )


class ReceiptViewSet(ReceptionConflictMixin, TenantViewSet):
    queryset = Receipt.objects.all()
    serializer_class = ReceiptSerializer
    permission_classes = [ReceptionPermission]
    operator_write = True
    http_method_names = ["get", "post", "head", "options"]
    uuid_filters = {"company": "company_id", "box": "box_id", "branch": "branch_id"}
    choice_filters = {"result": ["RECEIVED", "REJECTED"]}

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        actor = self.lock_actor()
        if request.query_params:
            raise ValidationError({"filtros": "Filters are only accepted on the collection GET."})
        try:
            key = uuid.UUID(request.headers.get("Idempotency-Key", ""))
        except (ValueError, TypeError, AttributeError):
            raise ValidationError(
                {"Idempotency-Key": "A UUID Idempotency-Key header is required."}
            ) from None
        incoming = ReceiptRequestSerializer(data=request.data)
        incoming.is_valid(raise_exception=True)
        data = incoming.validated_data
        receipt, replayed = receive_box(
            actor=actor,
            box_id=data["box"],
            branch_id=data["branch"],
            result=data["result"],
            reason=data["reason"],
            key=key,
            source=Receipt.Source.RECEIPT_API,
        )
        response = Response(
            self.get_serializer(receipt).data,
            status=status.HTTP_200_OK if replayed else status.HTTP_201_CREATED,
        )
        if replayed:
            response["Idempotent-Replayed"] = "true"
        return response


class BoxEventViewSet(TenantViewSet):
    queryset = BoxEvent.objects.all()
    serializer_class = BoxEventSerializer
    permission_classes = [ReceptionPermission]
    http_method_names = ["get", "head", "options"]
    uuid_filters = {"company": "company_id", "box": "box"}
    choice_filters = {"event_type": BoxEvent.EventType.values}
