from django.contrib.auth.forms import UserChangeForm as DjUserChangeForm
from django.contrib.auth.forms import UserCreationForm as DjUserCreationForm
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
            "security_ans_hash",
            "is_superuser"
            "is_staff",
        ]
