"""Private deterministic QR rendering and exact scoped identification. No file storage."""

import re
import uuid
from xml.etree import ElementTree as ET

import qrcode
from django.http import HttpResponse
from qrcode.image.svg import SvgPathImage
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.api import PrivateUserThrottle, is_global

from .serializers import BoxSerializer
from .views import BoxViewSet, ReceptionPermission

SVG = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG)


def payload(box):
    return f"logistech:box:{box.qr_code}"


def qr_svg(box):
    code = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, border=4)
    code.add_data(payload(box))
    code.make(fit=True)
    image = code.make_image(image_factory=SvgPathImage)
    root = ET.fromstring(image.to_string())
    root.insert(0, ET.Element(f"{{{SVG}}}rect", width="100%", height="100%", fill="white"))
    return ET.tostring(root, encoding="unicode")


def printable_label(box):
    root = ET.Element(
        f"{{{SVG}}}svg",
        {
            "width": "100mm",
            "height": "80mm",
            "viewBox": "0 0 400 320",
            "role": "img",
            "aria-label": f"LogisTech box label {box.internal_id}",
        },
    )
    ET.SubElement(root, f"{{{SVG}}}rect", width="400", height="320", fill="white")
    image = ET.fromstring(qr_svg(box))
    image.set("x", "90")
    image.set("y", "10")
    image.set("width", "220")
    image.set("height", "220")
    root.append(image)
    for y, size, text in [
        (244, 15, "LogisTech / Box identification"),
        (266, 13, box.internal_id),
        (286, 11, str(box.qr_code)),
        (306, 10, "Authentication required. This label grants no access."),
    ]:
        node = ET.SubElement(
            root,
            f"{{{SVG}}}text",
            {
                "x": "200",
                "y": str(y),
                "text-anchor": "middle",
                "font-size": str(size),
                "font-family": "monospace",
                "fill": "black",
            },
        )
        node.text = text
    return ET.tostring(root, encoding="unicode")


class BoxIdentificationViewSet(BoxViewSet):
    http_method_names = ["get", "head", "options"]

    def qr(self, request, *args, **kwargs):
        box = self.get_object()
        return Response(
            {
                "box": str(box.pk),
                "internal_id": box.internal_id,
                "qr_code": str(box.qr_code),
                "payload": payload(box),
                "svg": qr_svg(box),
            }
        )

    def label(self, request, *args, **kwargs):
        box = self.get_object()
        response = HttpResponse(printable_label(box), content_type="image/svg+xml; charset=utf-8")
        response["Content-Disposition"] = f'attachment; filename="{box.internal_id}-label.svg"'
        response["Content-Security-Policy"] = "default-src 'none'; style-src 'none'; sandbox"
        response["X-Content-Type-Options"] = "nosniff"
        return response


class IdentificationView(APIView):
    permission_classes = [IsAuthenticated, ReceptionPermission]
    throttle_classes = [PrivateUserThrottle]
    operator_write = False

    def get(self, request):
        params = request.query_params
        if set(params) != {"code"} or len(params.getlist("code")) != 1:
            raise ValidationError({"code": "Provide exactly one code parameter."})
        value = params["code"].strip()
        if not value or len(value) > 100:
            raise ValidationError({"code": "Enter a valid QR code or internal identifier."})
        if value.startswith("logistech:box:"):
            value = value.removeprefix("logistech:box:")
        if re.fullmatch(r"CJ-[A-F0-9]{32}", value.upper()):
            lookup = {"internal_id": value.upper()}
        else:
            try:
                lookup = {"qr_code": uuid.UUID(value)}
            except ValueError:
                raise ValidationError(
                    {"code": "Unsupported QR code or internal identifier."}
                ) from None
        query = BoxViewSet.queryset.all()
        if not is_global(request.user):
            query = query.filter(company_id=request.user.company_id)
        box = query.filter(**lookup).first()
        if box is None:
            raise NotFound("The box is unavailable in your authorized scope.")
        response = Response(BoxSerializer(box, context={"request": request}).data)
        response["Cache-Control"] = "no-store"
        return response
