from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from ninja import Schema
from ninja.security import APIKeyQuery, HttpBearer


class UserRegisterSchema(Schema):
    username: str
    password: str
    email: Optional[str] = None


class UserLoginSchema(Schema):
    username: str
    password: str


class TokenSchema(Schema):
    access_token: str
    token_type: str


def create_access_token(user_id: int) -> str:
    """Issues a signed JWT valid for 7 days."""
    expiration = datetime.now(timezone.utc) + timedelta(days=7)
    payload = {"user_id": user_id, "exp": expiration}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


def _resolve_user(token: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return get_user_model().objects.get(id=payload["user_id"])
    except (jwt.PyJWTError, KeyError, get_user_model().DoesNotExist):
        return None


class AuthBearer(HttpBearer):
    """Authenticates requests using the Authorization: Bearer header."""

    def authenticate(self, request, token):
        return _resolve_user(token)


class QueryTokenAuth(APIKeyQuery):
    """
    Authenticates requests using a ?token= query parameter.
    Needed for browser-initiated downloads, which cannot set custom headers.
    """

    param_name = "token"

    def authenticate(self, request, key):
        return _resolve_user(key)
    