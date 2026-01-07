import time
import uuid

from celery import shared_task
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 3, "countdown": 5},
)
def generate_dummy_file(self):
    """
    Celery-only task.
    Writes to MinIO using celery storage.
    """

    storage = default_storage

    time.sleep(3)

    content = b"hello from celery"
    path = f"reports/{uuid.uuid4()}.txt"

    storage.save(path, ContentFile(content))

    return path
