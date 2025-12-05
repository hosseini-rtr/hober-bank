import random
import string
from os import getenv
from typing import Any, Optional

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import UserManager as DjangoUserManager
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils.translation import gettext_lazy as _


def generate_username() -> str:
    bank_name = getenv("BANK_NAME")
    words = bank_name.split()
    prefix = "".join([word[0] for word in words]).upper()
    remaining_length = 12 - len(prefix) - 1

    random_char = "".join(
        random.choices(string.ascii_uppercase + string.digits, k=remaining_length)
    )
    username = f"{prefix}-{random_char}"
    return username


def validate_email_address(email: str) -> None:
    try:
        validate_email(email)
    except ValidationError:
        raise ValidationError(_("Enter a valid email address"))


class UserManager(DjangoUserManager):
    def _create_user(self, email: str, password: Optional[str], **other_fields: Any):
        if not email:
            raise ValueError(_("Email address is required"))
        if not password:
            raise ValueError(_("Password is required"))

        username = generate_username()
        email = self.normalize_email(email)
        validate_email_address(email)

        user = self.model(username=username, email=email, **other_fields)
        user.password = make_password(password)
        user.save(using=self._db)

    def create_user(
        self, email: str, password: Optional[str] = None, **other_fields: Any
    ):
        other_fields.setdefault("is_superuser", False)
        other_fields.setdefault("is_staff", False)
        return self._create_user(email, password, **other_fields)

    def create_superuser(
        self, email: str, password: Optional[str] = None, **other_fields: Any
    ):
        other_fields.setdefault("is_staff", True)
        other_fields.setdefault("is_superuser", True)

        if other_fields.get("is_staff") is not True:
            raise ValueError(_("Can not create this super user"))

        if other_fields.get("is_superuser") is not True:
            raise ValueError(_("Can not create this super user"))

        return self._create_user(email, password, **other_fields)
