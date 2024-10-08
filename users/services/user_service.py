from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.template.loader import render_to_string
from django.utils import timezone
from rest_framework.exceptions import NotFound

from users.constants import Roles
from users.models import User
from users.services.es_user_service import ESUserService
from users.services.jwt_service import JWTService
from users.services.profile_service import ProfileService
from users.tasks import send_email_task
from users.utils.simple_user_serializer import SimpleUserSerializer


class UserService:
    @classmethod
    def create(cls, validated, **kwargs) -> User:
        email = validated.get("email")
        password = validated.get("password")
        name = validated.get("name")
        with transaction.atomic():
            user = User.objects.create_user(email=email, password=password, name=name)
            ProfileService.create(user=user)

        serializer = SimpleUserSerializer(user)
        ESUserService.index.delay(serializer.data)
        return user

    @classmethod
    def get_by_email(
        cls,
        email,
        raise_exception=True,
        allow_deleted=False,
        allow_banned=False,
        **kwargs,
    ) -> User | None:
        try:
            user = User.objects.get(email=email, related_fields="profile")

            if not allow_deleted and user.deleted_at:
                raise NotFound("User not found")
            if not allow_banned and user.banned_at:
                raise NotFound("User not found")
            return user
        except Exception:
            if raise_exception:
                raise NotFound("User not found")
            return None

    @classmethod
    def get(
        cls,
        pk,
        raise_exception=True,
        allow_deleted=False,
        allow_banned=False,
        **kwargs,
    ) -> User | None:
        try:
            user = User.objects.get(id=pk, related_fields="profile")
            if not allow_deleted and user.deleted_at:
                raise NotFound("User not found")
            if not allow_banned and user.banned_at:
                raise NotFound("User not found")
            return user
        except Exception:
            if raise_exception:
                raise NotFound("User not found")
            return None

    @classmethod
    def login(cls, email, password, **kwargs) -> dict:
        user = cls.get_by_email(email)

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
    def update(cls, instance: User, validated: dict, partial=False, **kwargs) -> User:
        if partial:
            instance.name = validated.get("name", instance.name)
        else:
            instance.name = validated.get("name")

        cls.save_data(instance)
        return instance

    @classmethod
    def request_token(cls, email, **kwargs) -> str:
        cls.get_by_email(email)
        token = JWTService.create_verify_token(email)
        content = render_to_string("../templates/reset_password.html", {"token": token})
        send_email_task.delay([email], "Reset password", content)
        return token

    @classmethod
    def update_email(cls, validated_data, **kwargs) -> bool:
        token = validated_data.get("token")
        new_email = validated_data.get("email")

        email = JWTService.confirm_verify_token(token).get("email")
        instance = cls.get_by_email(email)
        if instance:
            instance.email = new_email
            cls.save_data(instance)
            return True
        return False

    @classmethod
    def update_password(cls, instance: User, validated_data: dict, **kwargs) -> bool:
        old_password = validated_data.get("old_password")
        new_password = validated_data.get("new_password")

        if not instance.check_password(old_password):
            raise PermissionDenied("Old password is incorrect")

        instance.set_password(new_password)
        cls.save_data(instance)
        return True

    @classmethod
    def update_password_with_token(cls, validated_data: dict, **kwargs) -> bool:
        token = validated_data.get("token")
        new_password = validated_data.get("new_password")

        email = JWTService.confirm_verify_token(token).get("email")
        instance = cls.get_by_email(email)
        if not instance:
            return False

        instance.set_password(new_password)
        cls.save_data(instance)
        return True

    @classmethod
    def delete(cls, pk, **kwargs) -> bool:
        instance = cls.get(pk, allow_banned=True, raise_exception=True)
        if not instance:
            return False
        instance.deleted_at = timezone.now()
        instance.save()
        ESUserService.delete.delay(str(pk))

        return True

    @classmethod
    def restore(cls, pk, **kwargs) -> bool:
        instance = cls.get(pk, allow_banned=True, allow_deleted=True)
        if not instance:
            return False

        instance.deleted_at = None
        instance.save()
        ESUserService.restore.delay(str(pk))

        return True

    @classmethod
    def ban(cls, pk, **kwargs) -> bool:
        instance = cls.get(pk)
        if not instance:
            return False

        instance.banned_at = timezone.now()
        cls.save_data(instance)

        return True

    @classmethod
    def unban(cls, pk, **kwargs) -> bool:
        instance = cls.get(pk, allow_banned=True)
        if not instance:
            return False

        instance.banned_at = None
        cls.save_data(instance)

        return True

    @classmethod
    def update_role(cls, user: User, instance: User, role, **kwargs) -> bool:
        if user.is_superuser:
            instance.role = role

        if user.role == Roles.ADMIN:
            if instance.role == Roles.ADMIN:
                raise PermissionDenied("You do not have permission to update role")
            if role == Roles.ADMIN:
                raise PermissionDenied("You cannot update to admin role")

            instance.role = role

        cls.save_data(instance)

        return True

    @classmethod
    def save_data(cls, instance: User):
        instance.save()
        serializer = SimpleUserSerializer(instance)
        ESUserService.update.delay(serializer.data)
        return instance
