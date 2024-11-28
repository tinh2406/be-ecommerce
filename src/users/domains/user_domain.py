from typing import Union

from django.core.exceptions import PermissionDenied
from django.utils import timezone
from rest_framework.exceptions import NotFound

from core.domains import BaseDomain
from users.constants import Roles
from users.models import User


class UserDomain(BaseDomain):
    manager = User.objects

    @classmethod
    def create(cls, validated_register_data: dict) -> User:
        return cls.manager.create_user(**validated_register_data)

    @classmethod
    def get_by_email(
        cls,
        email,
        raise_exception=True,
        allow_banned=False,
        **kwargs,
    ) -> Union[User, None]:
        try:
            user = User.objects.get(email=email, related_fields="profile")

            if user.deleted_at:
                raise NotFound("User not found")
            if not allow_banned and user.banned_at:
                raise NotFound("User not found")
            return user
        except Exception:
            if raise_exception:
                raise NotFound("User not found")
            return None

    @classmethod
    def update_password_by_token(
        cls, decoded_data: dict, new_password: str, **kwargs
    ) -> bool:
        email = decoded_data.get("email")
        instance = cls.get_by_email(email)
        if not instance:
            return False

        instance.set_password(new_password)
        instance.save()
        return True

    @classmethod
    def update_password(
        cls, user: User, old_password: str, new_password: str, **kwargs
    ) -> bool:
        if not user.check_password(old_password):
            return False

        user.set_password(new_password)
        user.save()
        return True

    @classmethod
    def update(cls, user: User, update_data: dict, **kwargs) -> User:

        user.name = update_data.get("name")
        user.save()
        return user

    @classmethod
    def update_email(cls, decoded_data: dict, new_email: str, **kwargs) -> bool:
        email = decoded_data.get("email")
        instance = cls.get_by_email(email)
        if not instance:
            return False

        instance.email = new_email
        instance.save()
        return True

    @classmethod
    def ban(cls, pk, **kwargs) -> bool:
        instance = cls.get(pk)
        if not instance:
            return False

        instance.banned_at = timezone.now()
        instance.save()
        cls.save_es(instance)

        return True

    @classmethod
    def unban(cls, pk, **kwargs) -> bool:
        instance = cls.get(pk, allow_banned=True)
        if not instance:
            return False

        instance.banned_at = None
        instance.save()
        cls.save_es(instance)

        return True

    @classmethod
    def update_role(cls, executor: User, executed_pk: str, role: str) -> bool:

        executed = cls.get(executed_pk)

        if executor.is_superuser:
            executed.role = role

        if executor.role == Roles.ADMIN:
            if executed.role == Roles.ADMIN:
                raise PermissionDenied("You do not have permission to update role")
            elif role == Roles.ADMIN:
                raise PermissionDenied("You cannot update to admin role")
            executed.role = role

        executed.save()
        return True
