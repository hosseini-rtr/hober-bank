from typing import Any, Type

from django.db.models import Model
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from loguru import logger

from config.settings.base import AUTH_USER_MODEL
from core_apps.user_profile.models import Party, PartyUserRole


@receiver(post_save, sender=AUTH_USER_MODEL)
def bootstrap_individual_party_for_user(
    sender: Type[Model],
    instance: Model,
    created: bool,
    **kwargs: Any,
) -> None:
    """
    Educational bootstrap only:
    - Each new user becomes an INDIVIDUAL Party
    - User is assigned as OWNER
    """

    if not created:
        return

    logger.info(f"Bootstrapping party for user {instance.pk}")

    party = Party.objects.create(
        party_type=Party.PartyType.INDIVIDUAL,
    )

    PartyUserRole.objects.create(
        party=party,
        user=instance,
        role=PartyUserRole.Role.OWNER,
        valid_from=timezone.now(),
    )
    logger.info(f"Created party {party.pk} for user {instance.pk}")
