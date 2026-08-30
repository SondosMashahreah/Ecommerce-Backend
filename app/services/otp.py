import secrets
from datetime import datetime, timedelta


def generate_otp() -> str:
    return f"{secrets.randbelow(1_000_000):06d}"


def get_otp_expiry():
    return datetime.utcnow() + timedelta(minutes=5)