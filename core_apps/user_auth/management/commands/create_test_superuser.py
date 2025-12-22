from django.conf import settings
from django.core.management.base import BaseCommand

from core_apps.user_auth.models import User


class Command(BaseCommand):
    help = "Create a static superuser for local/testing only"

    def handle(self, *args, **options):
        if not settings.DEBUG:
            self.stderr.write(
                self.style.ERROR("This command can only be run in DEBUG mode!")
            )
            return

        email = "ceo@test.com"
        password = "admin12345"
        security_question = User.SecurityQuestion.FAVORITE_COLOR
        security_answer = "red"

        if User.objects.filter(email=email).exists():
            self.stdout.write(self.style.WARNING("Test superuser already exists."))
            return

        user = User.objects.create_superuser(
            email=email,
            password=password,
            first_name="Test",
            last_name="Admin",
            id_number="111111",
            security_question=security_question,
            security_answer=security_answer,
            is_superuser=True,
        )  # type: ignore
        # user.save()
        self.stdout.write(self.style.SUCCESS(f"Superuser created!"))
