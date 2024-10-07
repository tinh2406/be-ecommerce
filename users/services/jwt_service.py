from datetime import datetime

import jwt
from django.conf import settings
from rest_framework.exceptions import ValidationError


class JWTService:

    @staticmethod
    def get_header():
        return {"alg": "HS256", "typ": "JWT"}

    @staticmethod
    def get_secret_key():
        return settings.SECRET_KEY

    @staticmethod
    def encode(user):
        payload = {"email": user.email, "iat": datetime.now().timestamp()}

        token = jwt.encode(payload, JWTService.get_secret_key(), algorithm="HS256")
        return token

    @staticmethod
    def decode(token, token_hours=12):
        payload = jwt.decode(token, JWTService.get_secret_key(), algorithms=["HS256"])

        iat = int(payload.get("iat"))
        email = payload.get("email")

        if iat + token_hours * 60 * 60 < datetime.now().timestamp():
            return None

        from .user_service import UserService

        user = UserService.get_by_email(email)
        if user:
            return user
        return None

    @staticmethod
    def create_verify_token(email):
        payload = {"email": email, "iat": datetime.now().timestamp()}
        token = jwt.encode(payload, JWTService.get_secret_key(), algorithm="HS256")
        return token

    @staticmethod
    def confirm_verify_token(token):
        try:
            payload = jwt.decode(
                token, JWTService.get_secret_key(), algorithms=["HS256"]
            )
            if payload.get("iat") + 5 * 60 < datetime.now().timestamp():
                raise ValidationError("Token expired")
            return {
                "email": payload.get("email"),
            }
        except Exception:
            raise ValidationError({"token": "Invalid token"})
