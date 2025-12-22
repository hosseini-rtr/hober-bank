from typing import Any

from django.contrib.auth.forms import UserChangeForm as DjUserChangeForm
from django.contrib.auth.forms import UserCreationForm as DjUserCreationForm
from django.contrib.auth.hashers import check_password, make_password
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .models import User


class UserCreationForm(DjUserCreationForm):
    class Meta:
        model = User
        fields = [
            "id_number",
            "first_name",
            "middle_name",
            "last_name",
            "email",
            "security_question",
            "security_answer",
            "is_superuser",
            "is_staff",
        ]

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise ValidationError(_("Email is exists."))
        return email

    def clean_id_number(self):
        id_number = self.cleaned_data.get("id_number")
        if User.objects.filter(id_number=id_number).exists():
            raise ValidationError(_("Id number is exists."))
        return id_number

    def clean(self) -> dict[str, Any]:
        cleaned_data = super().clean()
        is_superuser = cleaned_data.get("is_superuser")
        security_question = cleaned_data.get("security_question")
        security_answer = make_password(cleaned_data.get("security_answer"))

        if not is_superuser:
            if not security_question:
                self.add_error(
                    "security_question",
                    _("Security question is require for " "User Type"),
                )
            if not security_answer:
                self.add_error(
                    "security_answer",
                    _("Security answer is require for " "User Type"),
                )

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
        return user


class UserChangeForm(DjUserChangeForm):
    class Meta:
        model = User
        fields = [
            "id_number",
            "first_name",
            "middle_name",
            "last_name",
            "email",
            "security_question",
            "security_answer",
            "is_superuser",
            "is_active",
            "is_staff",
        ]

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.exclude(pk=self.instance.pk).filter(email=email).exists():
            raise ValidationError(_("Email is exists."))
        return email

    def clean_id_number(self):
        id_number = self.cleaned_data.get("id_number")
        if (
            User.objects.exclude(pk=self.instance.pk)
            .filter(id_number=id_number)
            .exists()
        ):
            raise ValidationError(_("Id Number is exists."))
        return id_number

    def clean(self) -> dict[str, Any]:
        cleaned_data = super().clean()
        is_superuser = cleaned_data.get("is_superuser")
        security_question = cleaned_data.get("security_question")
        security_answer = make_password(cleaned_data.get("security_answer"))

        if not is_superuser:
            if not security_question:
                self.add_error(
                    "security_question",
                    _("Security question is require for " "User Type"),
                )
            if not security_answer:
                self.add_error(
                    "security_answer",
                    _("Security answer is require for " "User Type"),
                )
        if self.errors or self.non_field_errors:

            print("=== FORM ERRORS AFTER CLEAN ===")
            print(self.errors)
            print(self.non_field_errors())

        return cleaned_data
