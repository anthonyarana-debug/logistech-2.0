from django.contrib.admin import AdminSite, ModelAdmin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.http import JsonResponse

from apps.accounts.models import User
from apps.accounts.throttles import LoginIPThrottle
from apps.boxes.models import Box
from apps.catalog.models import Category, Product
from apps.core.admin_presentation import MODEL_LABELS, EnglishAdminMixin
from apps.core.labels import CHOICE_LABELS
from apps.core.messages import message
from apps.organizations.models import Branch, Company


class OperationsAdminSite(AdminSite):
    site_header = "LogisTech · Restricted administration"
    site_title = "LogisTech"
    index_title = "Configuration resources"

    def get_app_list(self, request, app_label=None):
        apps = super().get_app_list(request, app_label)
        for app in apps:
            for model in app["models"]:
                labels = MODEL_LABELS.get(model["object_name"].lower())
                if labels:
                    model["name"] = labels[1].capitalize()
        return apps

    def login(self, request, extra_context=None):
        if request.method == "POST":
            throttle = LoginIPThrottle()
            if not throttle.allow_request(request, self):
                response = JsonResponse(
                    {"detalle": message("too_many_requests_please_try_again_later")}, status=429
                )
                response["Retry-After"] = str(max(1, int(throttle.wait())))
                return response
        return super().login(request, extra_context)

    def has_permission(self, request):
        user = request.user
        return (
            user.is_active
            and user.is_staff
            and user.is_superuser
            and user.role == User.Role.SUPERADMIN
        )


site = OperationsAdminSite(name="operations_admin")


class CreateUserForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            "email",
            "first_name",
            "last_name",
            "role",
            "company",
            "is_staff",
            "is_superuser",
            "is_active",
        )


class ChangeUserForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User
        fields = "__all__"


class LogisTechUserAdmin(EnglishAdminMixin, UserAdmin):
    def role_label(self, obj):
        """Display a role label without changing its persisted code or model choices."""
        return CHOICE_LABELS[obj.role]

    role_label.short_description = "Role"
    role_label.admin_order_field = "role"

    add_form = CreateUserForm
    form = ChangeUserForm
    ordering = ("email",)
    list_display = ("email", "role_label", "company", "is_active")
    search_fields = ("email", "first_name", "last_name")
    readonly_fields = ("created_at", "last_login")
    fieldsets = (
        ("Identity", {"fields": ("email", "password", "first_name", "last_name")}),
        ("Authorization", {"fields": ("role", "company", "is_active", "is_staff", "is_superuser")}),
        ("Dates", {"fields": ("created_at", "last_login")}),
    )
    add_fieldsets = (
        (
            "New user",
            {
                "fields": (
                    "email",
                    "password1",
                    "password2",
                    "first_name",
                    "last_name",
                    "role",
                    "company",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                )
            },
        ),
    )


class CompanyResourceAdmin(EnglishAdminMixin, ModelAdmin):
    list_display = ("id", "company", "created_at")
    list_select_related = ("company",)
    readonly_fields = ("id", "created_at")

    def get_readonly_fields(self, request, obj=None):
        return (*self.readonly_fields, "company") if obj else self.readonly_fields


site.register(User, LogisTechUserAdmin)
site.register(Company, type("CompanyAdmin", (EnglishAdminMixin, ModelAdmin), {}))
for model in (Branch, Category, Product, Box):
    site.register(model, CompanyResourceAdmin)
