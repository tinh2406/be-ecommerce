from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.template.loader import render_to_string
from django.utils import timezone
from rest_framework.exceptions import NotFound

from users.constants import Roles
from users.models import User
from users.services.es_user_service import ESUserService
from users.services.profile_service import ProfileService
from users.services.jwt_service import JWTService
from users.tasks import send_email_task


class UserService:
    @classmethod
    def create(cls, validated, **kwargs) -> User:
        email = validated.get('email')
        password = validated.get('password')
        name = validated.get('name')
        with transaction.atomic():
            user = User.objects.create_user(email=email, password=password, name=name)
            ProfileService.create(user)
            ESUserService.index(user)
        key_cache = f'user_{user.email}'
        cache.set(key_cache, user, timeout=60)
        return user

    @classmethod
    def get_by_email(cls, email, raise_exception=True, allow_deleted=False, allow_banned=False,
                     use_cache=True, **kwargs) -> User | None:
        try:
            cache_key = f'user_{email}'

            if use_cache:
                user_cache = cache.get(cache_key)
                if user_cache:
                    return user_cache

            user = User.objects.get(email=email)

            if not allow_deleted and user.deleted_at:
                raise NotFound('User not found')
            if not allow_banned and user.banned_at:
                raise NotFound('User not found')
            cache.set(cache_key, user, timeout=60)
            return user
        except Exception as e:
            if raise_exception:
                raise NotFound('User not found')
            return None

    @classmethod
    def get(cls, pk, raise_exception=True, allow_deleted=False, allow_banned=False, use_cache=True,
            **kwargs) -> User | None:
        try:
            cache_key = f'user_{pk}'
            if use_cache:
                user_cache = cache.get(cache_key)
                if user_cache:
                    return user_cache
            user = User.objects.get(pk=pk)
            if not allow_deleted and user.deleted_at:
                raise NotFound('User not found')
            if not allow_banned and user.banned_at:
                raise NotFound('User not found')
            cache.set(cache_key, user, timeout=60)
            return user
        except Exception as e:
            if raise_exception:
                raise NotFound('User not found')
            return None

    @classmethod
    def login(cls, email, password, **kwargs) -> dict:
        user = cls.get_by_email(email)
        if not user.check_password(password):
            raise NotFound('User not found')
        return {
            'user': {
                'id': str(user.id),
                'name': user.name,
                'email': user.email,
                'role': user.role,
            },
            'token': JWTService.encode(user)
        }

    @classmethod
    def update(cls, instance: User, validated: dict, partial=False, **kwargs) -> User:
        if partial:
            instance.name = validated.get('name', instance.name)
        else:
            instance.name = validated.get('name')
        instance.save()
        ESUserService.update(instance, instance.profile)

        cls.save_cache(instance, timeout=60)
        return instance

    @classmethod
    def save_cache(cls, instance, timeout=60, **kwargs):
        cache_key = f'user_{instance.id}'
        cache.set(cache_key, instance, timeout=timeout)
        cache_key = f'user_{instance.email}'
        cache.set(cache_key, instance, timeout=timeout)

    @classmethod
    def request_token(cls, email, **kwargs) -> str:
        user = cls.get_by_email(email)
        token = JWTService.create_verify_token(email)
        content = render_to_string('../templates/reset_password.html', {
            'token': token
        })
        send_email_task.delay([email], 'Reset password', content)
        return token

    @classmethod
    def update_email(cls, validated_data, **kwargs) -> bool:
        token = validated_data.get('token')
        new_email = validated_data.get('email')

        email = JWTService.confirm_verify_token(token).get('email')
        instance = cls.get_by_email(email)
        instance.email = new_email
        instance.save()
        ESUserService.update(instance, instance.profile)
        cls.save_cache(instance, timeout=60)
        cache.delete(f'user_{email}')
        return True

    @classmethod
    def update_password(cls, instance: User, validated_data: dict, **kwargs) -> bool:
        old_password = validated_data.get('old_password')
        new_password = validated_data.get('new_password')

        if not instance.check_password(old_password):
            raise PermissionDenied('Old password is incorrect')

        instance.set_password(new_password)
        instance.save()
        cls.save_cache(instance, timeout=60)
        return True

    @classmethod
    def update_password_with_token(cls, validated_data: dict, **kwargs) -> bool:
        token = validated_data.get('token')
        new_password = validated_data.get('new_password')

        email = JWTService.confirm_verify_token(token).get('email')
        instance = cls.get_by_email(email)
        instance.set_password(new_password)
        instance.save()
        cls.save_cache(instance, timeout=60)
        return True

    @classmethod
    def delete(cls, pk, **kwargs) -> bool:
        instance = cls.get(pk, allow_banned=True)

        try:
            instance.delete()
            ESUserService.delete(str(pk))

        except Exception as e:
            instance.deleted_at = timezone.now()
            instance.save()
            ESUserService.update(user=instance, profile=instance.profile)
        cache.delete(f'user_{str(pk)}')
        cache.delete(f'user_{instance.email}')
        return True

    @classmethod
    def restore(cls, pk, **kwargs) -> bool:
        instance = cls.get(pk, allow_banned=True, allow_deleted=True)
        instance.deleted_at = None
        instance.save()
        ESUserService.update(user=instance, profile=instance.profile)
        cls.save_cache(instance, timeout=60)
        return True

    @classmethod
    def ban(cls, pk, **kwargs) -> bool:
        instance = cls.get(pk)
        instance.banned_at = timezone.now()
        instance.save()
        ESUserService.update(user=instance, profile=instance.profile)
        cache.delete(f'user_{str(pk)}')
        cache.delete(f'user_{instance.email}')
        return True

    @classmethod
    def unban(cls, pk, **kwargs) -> bool:
        instance = cls.get(pk, allow_banned=True)
        instance.banned_at = None
        instance.save()
        ESUserService.update(user=instance, profile=instance.profile)
        cls.save_cache(instance, timeout=60)
        return True

    @classmethod
    def update_role(cls, user: User, instance: User, role, **kwargs) -> bool:
        if user.is_superuser:
            instance.role = role

        if user.role == Roles.ADMIN:
            if instance.role == Roles.ADMIN:
                raise PermissionDenied('You do not have permission to update role')
            if role == Roles.ADMIN:
                raise PermissionDenied('You cannot update to admin role')

            instance.role = role

        instance.save()
        ESUserService.update(instance, instance.profile)
        cls.save_cache(instance, timeout=60)
        return True


