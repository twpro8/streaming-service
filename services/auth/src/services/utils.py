import secrets
import string


def generate_upper_code(length: int = 6) -> str:
    alphabet = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def get_verification_key(email: str) -> str:
    return f"verification:{email}"
