from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("El correo es obligatorio.")
        user = self.model(email=email.strip().lower(), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("role", self.model.Role.SUPERADMIN)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        if (
            extra_fields["role"] != self.model.Role.SUPERADMIN
            or not extra_fields["is_staff"]
            or not extra_fields["is_superuser"]
            or not extra_fields["is_active"]
            or extra_fields.get("company") is not None
            or extra_fields.get("company_id") is not None
        ):
            raise ValueError("El superadministrador requiere flags coherentes y alcance global.")
        return self.create_user(email, password, **extra_fields)
