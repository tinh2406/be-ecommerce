from django.db import transaction
from rest_framework.exceptions import NotFound

from users.models import User
from users.serializers import UserSerializer
from users.services import ESUserService, JWTService, ProfileService, UserService
from users.tasks import send_email_task


class AuthDomain:
    @classmethod
    def register(cls, register_data: dict) -> User:

        with transaction.atomic():
            user = UserService.create(register_data)
            ProfileService.create(user=user)
            ESUserService.index.delay(UserSerializer(user).data)
        return user

    @classmethod
    def login(cls, email, password, **kwargs) -> dict:
        user = UserService.get_by_email(email)

        if not user or not user.check_password(password):
            raise NotFound("User not found")
        return {
            "user": {
                "id": str(user.id),
                "name": user.name,
                "email": user.email,
                "role": user.role,
            },
            "token": JWTService.encode(user),
        }

    @classmethod
    def request_token(cls, email, **kwargs) -> str:
        UserService.get_by_email(email)
        token = JWTService.create_verify_token(email)
        send_email_task.delay([email], "Reset password", token)
        return token

    @classmethod
    def reset_password_by_token(cls, token, new_password, **kwargs) -> bool:
        decoded_data = JWTService.confirm_verify_token(token)
        return UserService.update_password_by_token(decoded_data, new_password)
