from django.core.cache import cache
from django.db import transaction
from rest_framework.exceptions import NotFound

from users.document import UserDocument
from users.models import User
from users.services.profile_service import ProfileService
from users.services.jwt_service import JWTService
class UserService:
    @classmethod
    def create(cls, validated, **kwargs) -> User:
        email = validated.get('email')
        password = validated.get('password')
        name = validated.get('name')
        with transaction.atomic():
            user = User.objects.create_user(email=email, password=password, name=name)
            profile = ProfileService.create(user)
            user_doc = UserDocument(
                meta={'id': str(user.id)},
                name=user.name,
                email=user.email,
                role=user.role,
                created_at=user.created_at,
            )
            user_doc.save()
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

        user_doc = UserDocument.get(id=str(instance.id))
        user_doc.update(
            name=instance.name,
        )

        cls.save_cache(instance, timeout=60)
        return instance

    @classmethod
    def save_cache(cls, instance, timeout=60, **kwargs):
        cache_key = f'user_{instance.id}'
        cache.set(cache_key, instance, timeout=timeout)
        cache_key = f'user_{instance.email}'
        cache.set(cache_key, instance, timeout=timeout)