# built-in modules
import os
from datetime import datetime, timedelta, timezone

# pip modules
from fastapi import Response
from passlib.hash import bcrypt
import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError


def hash_password(password: str) -> str:
    return bcrypt.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.verify(plain_password, hashed_password)


def generate_jwt_token(data: dict) -> str:
    payload = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=int(os.getenv("JWT_EXPIRATION_TIME"))
    )
    payload.update({"exp": expire})

    token = jwt.encode(
        payload=payload,
        key=os.getenv("JWT_SECRET_KEY"),
        algorithm=os.getenv("JWT_ALGORITHM"),
    )

    return token


def decode_jwt_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            os.getenv("JWT_SECRET_KEY"),
            algorithms=[os.getenv("JWT_ALGORITHM")],
            options={
                "require": ["exp"],
                "verify_exp": True,
            },
        )
        return payload
    except ExpiredSignatureError:
        raise Exception("Unauthorized - Token has expired")
    except InvalidTokenError:
        raise Exception("Unauthorized - Invalid token")
