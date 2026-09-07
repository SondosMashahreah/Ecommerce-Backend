import os
from datetime import datetime, timedelta, timezone 

import jwt
from dotenv import load_dotenv
from pwdlib import PasswordHash

load_dotenv()

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
)

REFRESH_TOKEN_EXPIRE_DAYS = int(
    os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7")
)

password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(
        plain_password,
        hashed_password
    )


def create_access_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(user_id),
        "type": "access",
        "exp": expire
    }

    return jwt.encode(
        payload,
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM
    )


def create_refresh_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        days=REFRESH_TOKEN_EXPIRE_DAYS
    )

    payload = {
        "sub": str(user_id),
        "type": "refresh",
        "exp": expire
    }

    return jwt.encode(
        payload,
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM
    )


def decode_access_token(token: str):
    try:
        payload = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM]
        )

        if payload.get("type") != "access":
            return None

        return payload

    except jwt.InvalidTokenError:
        return None


def decode_refresh_token(token: str):
    try:
        payload = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM]
        )

        if payload.get("type") != "refresh":
            return None

        return payload

    except jwt.InvalidTokenError:
        return None