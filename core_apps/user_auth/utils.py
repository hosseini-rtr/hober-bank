import random
import string


def generate_otp(length) -> str:
    return "".join(random.choices(string.digits, k=length))
