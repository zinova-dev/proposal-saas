from datetime import datetime, timedelta
from typing import Optional
from django.conf import settings
from ninja import Schema
from ninja.security import HttpBearer
import jwt
from django.contrib.auth import get_user_model

# --- Schemas ---

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

# --- Authentication Logic ---

class AuthBearer(HttpBearer):
    def authenticate(self, request, token):
        # Check if token is passed in the query params (for PDF download)
        if not token:
            token = request.GET.get('token')
            
        if not token:
            return None

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            User = get_user_model()
            user = User.objects.get(id=payload["user_id"])
            return user
        except Exception:
            return None

def create_access_token(user_id: int):
    """
    Generates a JWT token valid for 7 days.
    """
    expiration = datetime.utcnow() + timedelta(days=7)
    payload = {
        "user_id": user_id,
        "exp": expiration
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
