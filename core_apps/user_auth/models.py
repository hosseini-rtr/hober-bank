import random
import uuid

from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .emails import send_account_locked_email
from .managers import UserManager
from .utils import generate_otp


# TODO: Separate OTP to UserOTP model
class User(AbstractUser):
    class SecurityQuestion(models.TextChoices):
        FAVORITE_COLOR = ("favorite_color", _("What is your favorite color?"))
        FAVORITE_CITY = ("favorite_city", _("What is your city color?"))
        CHILDHOOD_FRIEND = (
            "childhood_friend",
            _("What is your childhood friend name?"),
        )

    class AccountStatus(models.TextChoices):
        ACTIVE = ("active", _("Active"))
        LOCKED = ("locked", _("Locked"))

    class RoleChoices(models.TextChoices):
        CUSTOMER = ("customer", _("Customer"))
        ACCOUNT_EXECUTIVE = ("account_executive", _("account executive"))
        TELLER = ("teller", _("Teller"))
        BRANCH_MANAGER = ("branch_manager", _("Branch manager"))

    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, db_index=True
    )
    username = models.CharField(
        _("Username"), max_length=12, unique=True, editable=False
    )
    security_question = models.CharField(
        _("Security Question"), max_length=150, choices=SecurityQuestion.choices
    )
    security_answer = models.CharField(max_length=128)
    email = models.EmailField(_("Email"), unique=True, db_index=True)
    first_name = models.CharField(_("First name"), max_length=30)
    middle_name = models.CharField(
        _("Middle name"), max_length=30, blank=True, null=True
    )
    last_name = models.CharField(_("Last name"), max_length=30)
    id_number = models.CharField(max_length=20, unique=True)

    account_status = models.CharField(
        _("Account status"),
        max_length=30,
        choices=AccountStatus.choices,
        default=AccountStatus.ACTIVE,
    )
    role = models.CharField(
        _("Role"),
        choices=RoleChoices.choices,
        default=RoleChoices.CUSTOMER,
        max_length=55,
    )
    last_failed_login = models.DateTimeField(null=True, blank=True)
    otp_hash = models.CharField(max_length=128, blank=True)
    otp_expiry_time = models.DateTimeField(null=True, blank=True)
    login_attempts = models.PositiveSmallIntegerField(default=0)

    objects = UserManager()
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = [
        "first_name",
        "last_name",
        "id_number",
        "security_question",
        "security_answer",
    ]

    def set_otp(self):
        otp = f"{random.randint(100000, 999999)}"
        self.otp_hash = make_password(otp)
        self.otp_expiry_time = timezone.now() + settings.OTP_EXPIRATION
        self.login_attempts = 0
        self.save(update_fields=["otp_hash", "otp_expiry_time", "otp_attempts"])
        return otp

    def clear_otp(self):
        self.otp_hash = ""
        self.otp_expiry_time = None
        self.login_attempts = 0
        self.save(update_fields=["otp_hash", "otp_expiry_time", "otp_attempts"])

    def verify_otp(self, otp: str) -> bool:
        if not self.otp_expiry_time:
            return False

        if timezone.now() > self.otp_expiry_time:
            self.clear_otp()
            return False

        if self.login_attempts >= settings.MAX_OTP_ATTEMPTS:
            self.clear_otp()
            return False

        if check_password(otp, self.otp_hash):
            self.clear_otp()
            return True

        self.login_attempts += 1
        self.save(update_fields=["otp_attempts"])
        return False

    def set_security_answer(self, answer: str):
        normalized = answer.strip().lower()
        self.security_answer = make_password(normalized)

    def verify_security_answer(self, answer: str) -> bool:
        normalized = answer.strip().lower()
        return check_password(normalized, self.security_answer)

    def handle_failed_login_attempts(self) -> None:
        self.login_attempts += 1
        self.last_failed_login = timezone.now()
        if self.login_attempts >= settings.MAX_OTP_ATTEMPTS:
            self.account_status = self.AccountStatus.LOCKED

        send_account_locked_email(self)
        self.save(update_fields=["login_attempts", "last_failed_login"])

    def reset_failed_login_attempts(self):
        self.login_attempts = 0
        self.last_failed_login = None
        self.account_status = self.AccountStatus.ACTIVE
        self.save(update_fields=["login_attempts", "last_failed_login"])

    def unlock_account(self) -> None:
        if self.account_status == self.AccountStatus.LOCKED:
            self.account_status = self.AccountStatus.ACTIVE
            self.last_failed_login = None
            self.login_attempts = 0
            self.save(
                update_fields=["account_status", "login_attempts", "last_failed_login"]
            )

    @property
    def is_locked_out(self) -> bool:
        if self.account_status == self.AccountStatus.ACTIVE:
            if (
                self.last_failed_login
                and (timezone.now() - self.last_failed_login)
                > settings.LOCKOUT_DURATION
            ):
                self.unlock_account()
                return False
            return True
        return False

    @property
    def full_name(self) -> str:
        full_name = " ".join(
            part for part in [self.first_name, self.middle_name, self.last_name] if part
        )
        return full_name.title().strip()

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        ordering = ["-date_joined"]

    def has_role(self, role_name: str) -> bool:
        return hasattr(self, role_name) and self.role == role_name

    def __str__(self) -> str:
        return f"{self.full_name} - {self.get_role_display()}"  # type: ignore
