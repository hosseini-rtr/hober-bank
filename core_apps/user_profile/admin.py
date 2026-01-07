from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import IndividualProfile, LegalProfile, NextOfKin, Party, PartyUserRole


class NextOfKinInline(admin.TabularInline):
    model = NextOfKin
    extra = 1
    fields = ("title", "first_name", "last_name", "relationship", "is_primary")
    verbose_name = _("Next of Kin")
    verbose_name_plural = _("Next of Kin")


@admin.register(IndividualProfile)
class IndividualProfileAdmin(admin.ModelAdmin):
    list_display = (
        "party_id",
        "title",
        "phone_number",
        "email",
        "date_of_birth",
        "fraud_alert",
        "photo_preview",
    )
    list_filter = ("gender", "fraud_alert", "identification_type")
    search_fields = ("party__id", "phone_number", "email")
    readonly_fields = ("party",)

    fieldsets = (
        (_("Party Link"), {"fields": ("party",)}),
        (
            _("Personal Details"),
            {"fields": ("title", "gender", "date_of_birth", "nationality")},
        ),
        (
            _("Identification"),
            {"fields": ("identification_type", "photo", "signature")},
        ),
        (_("Contact"), {"fields": ("phone_number", "email")}),
        (_("Security"), {"fields": ("fraud_alert",)}),
    )

    inlines = [NextOfKinInline]

    def party_id(self, obj) -> str:
        return obj.party_id

    party_id.short_description = _("Party ID")

    def email(self, obj) -> str:
        return obj.email if hasattr(obj, "email") else ""

    email.short_description = _("Email")

    def photo_preview(self, obj) -> str:
        if obj.photo and hasattr(obj.photo, "url"):
            return format_html(
                f'<img src="{obj.photo.url}" width="50" height="50" style="object-fit:cover;" />'
            )
        return "No Photo"

    photo_preview.short_description = _("Photo")


@admin.register(LegalProfile)
class LegalProfileAdmin(admin.ModelAdmin):
    list_display = (
        "party_id",
        "incorporation_date",
        "country_of_incorporation",
    )
    search_fields = ("party__id",)
    readonly_fields = ("party",)

    fieldsets = (
        (_("Party Link"), {"fields": ("party",)}),
        (
            _("Registration Details"),
            {
                "fields": (
                    "incorporation_date",
                    "country_of_incorporation",
                )
            },
        ),
        (
            _("Company Details"),
            {"fields": ("company_name", "industry", "annual_revenue")},
        ),
    )

    def party_id(self, obj) -> str:
        return obj.party_id

    party_id.short_description = _("Party ID")


@admin.register(Party)
class PartyAdmin(admin.ModelAdmin):
    list_display = ("id", "party_type", "created_at", "verified_at")
    list_filter = ("party_type", "verified_at")
    search_fields = ("id",)
    readonly_fields = ("created_at", "verified_at", "verified_by")

    def has_add_permission(self, request):
        return False


@admin.register(PartyUserRole)
class PartyUserRoleAdmin(admin.ModelAdmin):
    list_display = ("party", "user", "role", "is_active", "valid_from", "valid_to")
    list_filter = ("role", "is_active")
    search_fields = ("party__id", "user__email")
    list_editable = ("is_active", "valid_to", "role")
    readonly_fields = ("valid_from",)


@admin.register(NextOfKin)
class NextOfKinAdmin(admin.ModelAdmin):
    list_display = ("full_name", "relationship", "profile", "is_primary")
    list_filter = ("is_primary", "relationship")
    search_fields = ("first_name", "last_name", "profile__party_id")

    def full_name(self, obj) -> str:
        return f"{obj.first_name} {obj.last_name}"

    full_name.short_description = _("Full Name")
