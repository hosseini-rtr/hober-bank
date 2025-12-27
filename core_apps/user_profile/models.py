import uuid
from typing import Any

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField
from phonenumber_field.modelfields import PhoneNumberField

from core_apps.common.models import TimeStampedModel

from .utils import user_photo_path, user_signature_path

User = get_user_model()


# Party = Owner of rights
class Party(TimeStampedModel):
    class PartyType(models.TextChoices):
        INDIVIDUAL = "individual", _("Individual")
        LEGAL = "legal", _("Legal")

    party_type = models.CharField(
        max_length=20,
        choices=PartyType.choices,
    )

    identification_number = models.CharField(max_length=50, null=True, blank=True)
    tax_id = models.CharField(max_length=50, null=True, blank=True)

    country_of_registration = CountryField(null=True, blank=True)

    verified_at = models.DateTimeField(null=True, blank=True)
    verified_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL
    )

    def __str__(self):
        return f"Party({self.party_type})"


class PartyUserRole(models.Model):
    class Role(models.TextChoices):
        OWNER = "OWNER", _("Owner")
        SIGNATORY = "SIGNATORY", _("Signatory")
        VIEWER = "VIEWER", _("Viewer")

    party = models.ForeignKey(Party, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    role = models.CharField(max_length=20, choices=Role.choices)

    is_active = models.BooleanField(default=True)
    valid_from = models.DateTimeField(default=timezone.now)
    valid_to = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("party", "user", "role")

    def __str__(self):
        return f"{self.user} -> {self.party} ({self.role})"


class IndividualProfile(TimeStampedModel):
    party = models.OneToOneField(
        Party,
        on_delete=models.CASCADE,
        related_name="individual_profile",
        limit_choices_to={"party_type": Party.PartyType.INDIVIDUAL},
    )

    title = models.CharField(max_length=10, choices=SalutationChoices.choices)
    gender = models.CharField(max_length=10, choices=GenderChoices.choices)
    date_of_birth = models.DateField()

    phone_number = PhoneNumberField(unique=True)
    email = models.EmailField(unique=True)

    country_of_birth = CountryField()
    nationality = CountryField()

    identification_type = models.CharField(
        max_length=20, choices=IdentificationTypeChoices.choices
    )

    photo = models.ImageField(upload_to=user_photo_path)
    signature = models.ImageField(upload_to=user_signature_path)

    fraud_alert = models.BooleanField(default=False)

    def __str__(self):
        return f"IndividualProfile({self.party_id})"


class NextOfKin(TimeStampedModel):
    class SalutationChoices(models.TextChoices):
        MR = ("Mr", _("Mr"))
        MS = ("Ms", _("Ms"))
        DR = ("Dr", _("Dr"))
        PROF = ("Prof", _("Prof"))

    class GenderChoices(models.TextChoices):
        MALE = ("male", _("Male"))
        FEMALE = ("female", _("Female"))

    profile = models.ForeignKey(
        IndividualProfile,
        on_delete=models.CASCADE,
        related_name="next_of_kin",
    )
    title = models.CharField(
        _("Salutation"),
        max_length=10,
        choices=SalutationChoices.choices,
        null=True,
        blank=True,
    )
    first_name = models.CharField(_("First Name"), max_length=150)
    last_name = models.CharField(_("Last Name"), max_length=150)
    other_names = models.CharField(
        _("Other Names"), max_length=150, null=True, blank=True
    )
    date_of_birth = models.DateField(_("Date of Birth"), null=True, blank=True)
    gender = models.CharField(
        _("Gender"),
        max_length=10,
        choices=GenderChoices.choices,
        null=True,
        blank=True,
    )
    relationship = models.CharField(_("Relationship"), max_length=100)
    email = models.EmailField(_("Email"), null=True, blank=True)
    phone_number = PhoneNumberField(_("Phone Number"), null=True, blank=True)
    city = models.CharField(_("City"), max_length=100, null=True, blank=True)
    country = CountryField(_("Country"), null=True, blank=True)
    is_primary = models.BooleanField(_("Is Primary Next of Kin"), default=False)

    def clean(self) -> None:
        super().clean()
        if self.is_primary:
            primary_kin = NextOfKin.objects.filter(
                profile=self.profile, is_primary=True
            ).exclude(id=self.id)
            if primary_kin.exists():
                raise ValidationError(
                    {
                        "is_primary": _(
                            "There is already a primary next of kin for this profile."
                        )
                    }
                )

    def save(self, *args: Any, **kwargs: Any) -> None:
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"NextOfKin({self.first_name} {self.last_name})"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["profile", "is_primary"],
                condition=models.Q(is_primary=True),
                name="unique_primary_next_of_kin_per_profile",
            )
        ]


class LegalProfile(TimeStampedModel):
    party = models.OneToOneField(
        Party,
        on_delete=models.CASCADE,
        related_name="legal_profile",
        limit_choices_to={"party_type": Party.PartyType.LEGAL},
    )

    incorporation_date = models.DateField(null=True, blank=True)
    country_of_incorporation = CountryField(null=True, blank=True)

    def __str__(self):
        return f"LegalProfile({self.party_id})"
