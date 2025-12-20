import random

from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.utils import timezone


def generate_otp():
    return f"{random.randint(100000, 999999)}"



