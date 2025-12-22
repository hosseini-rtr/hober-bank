from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from .forms import UserChangeForm, UserCreationForm
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    readonly_fields = ("username",)
    form = UserChangeForm
    add_form = UserCreationForm
    model = User
    list_display = ["email", "id_number", "full_name", "is_staff", "is_superuser"]
    fieldsets = (
        (
            _("Auth Credentials"),
            {
                "fields": ("username", "email", "password"),
            },
        ),
        (
            _("Personal Info"),
            {
                "fields": (
                    "first_name",
                    "middle_name",
                    "last_name",
                    "id_number",
                    "role",
                )
            },
        ),
        (
            _("Account status"),
            {"fields": ("account_status", "login_attempts", "last_failed_login")},
        ),
        (_("Security"), {"fields": ("security_question", "security_answer")}),
        (
            _("Permissions and Groups"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (
            _("Important dates"),
            {
                "fields": (
                    "last_login",
                    "date_joined",
                )
            },
        ),
    )
    search_fields = [
        "email",
        "username",
        "id_number",
        "first_name",
        "last_name",
        "role",
    ]
    ordering = ["id_number"]
