from uuid import uuid4


def user_photo_path(instance, filename):
    """Generate path for each user base uuid

    Args:
        instance (_type_): _description_
        filename (_type_): _description_
    """
    ext = filename.split(".")[-1]
    return f"user/photos/{instance.id}/{uuid4()}.{ext}"


def user_signature_path(instance, filename):
    """Generate path for each user base uuid

    Args:
        instance (_type_): _description_
        filename (_type_): _description_
    """
    ext = filename.split(".")[-1]
    return f"user/photos/سثsignatures/{instance.id}/{uuid4()}.{ext}"
