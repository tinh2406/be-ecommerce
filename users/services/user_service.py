from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.template.loader import render_to_string
from django.utils import timezone
from rest_framework.exceptions import NotFound
from elasticsearch_dsl.query import Exists, Range, Term

from users.constants import Roles
from users.document import UserDocument
from users.models import User
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
            profile = ProfileService.create(user)
            user_doc = UserDocument(
                meta={'id': str(user.id)},
                name=user.name,
                email=user.email,
                role=user.role,
                id=str(user.id),
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
        user_doc = UserDocument.get(id=str(instance.id))
        user_doc.update(
            email=new_email
        )
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
        user_doc = UserDocument.get(id=str(pk))

        try:
            instance.delete()
            user_doc.delete()

        except Exception as e:
            instance.deleted_at = timezone.now()
            instance.save()
            user_doc.update(
                deleted_at=instance.deleted_at
            )
        cache.delete(f'user_{str(pk)}')
        cache.delete(f'user_{instance.email}')
        return True

    @classmethod
    def restore(cls, pk, **kwargs) -> bool:
        instance = cls.get(pk, allow_banned=True, allow_deleted=True)
        instance.deleted_at = None
        instance.save()
        user_doc = UserDocument.get(id=str(instance.id))
        user_doc.update(
            deleted_at=None
        )
        cls.save_cache(instance, timeout=60)
        return True

    @classmethod
    def ban(cls, pk, **kwargs) -> bool:
        instance = cls.get(pk)
        instance.banned_at = timezone.now()
        instance.save()
        user_doc = UserDocument.get(id=str(instance.id))
        user_doc.update(
            banned_at=instance.banned_at
        )
        cache.delete(f'user_{str(pk)}')
        cache.delete(f'user_{instance.email}')
        return True

    @classmethod
    def unban(cls, pk, **kwargs) -> bool:
        instance = cls.get(pk, allow_banned=True)
        instance.banned_at = None
        instance.save()
        user_doc = UserDocument.get(id=str(instance.id))
        user_doc.update(
            banned_at=None
        )
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
        user_doc = UserDocument.get(id=str(instance.id))
        user_doc.update(
            role=instance.role
        )
        cls.save_cache(instance, timeout=60)
        return True

    @classmethod
    def list(cls, query_params, paginate=True, **kwargs):

        search = UserDocument.search()

        # Lấy các tham số truy vấn
        text = query_params.get('text')
        role = query_params.get('role')
        gender = query_params.get('gender')
        birthday = query_params.get('birthday')
        birthday_from = query_params.get('birthday_from')
        birthday_to = query_params.get('birthday_to')
        is_all = query_params.get('is_all')
        is_deleted = query_params.get('is_deleted')
        is_banned = query_params.get('is_banned')
        created_from = query_params.get('created_from')
        created_to = query_params.get('created_to')
        delete_from = query_params.get('delete_from')
        delete_to = query_params.get('delete_to')
        banned_from = query_params.get('banned_from')
        banned_to = query_params.get('banned_to')
        order_by = query_params.get('order_by') if query_params.get('order_by') else 'created_at'
        order_type = query_params.get('order_type') if query_params.get('order_type') else 'desc'
        page_size = query_params.get('page_size', 10)
        page = query_params.get('page', 1)
        skip = query_params.get('skip')

        if is_all:
            if is_deleted is not None:
                if is_deleted:
                    query = Exists(field='deleted_at')
                else:
                    query = ~Exists(field='deleted_at')
                search = search.query(query)
            if is_banned is not None:
                if is_banned:
                    query = Exists(field='banned_at')
                else:
                    query = ~Exists(field='banned_at')
                search = search.query(query)
            if delete_from:
                search = search.query(Range(deleted_at={'gte': delete_from}))
            if delete_to:
                search = search.query(Range(deleted_at={'lte': delete_to}))
            if banned_from:
                search = search.query(Range(banned_at={'gte': banned_from}))
            if banned_to:
                search = search.query(Range(banned_at={'lte': banned_to}))
        else:
            # Lọc những bản ghi không bị xóa hoặc banned
            search = search.filter(
                "bool",
                must_not=[
                    {"exists": {"field": "deleted_at"}},
                    {"exists": {"field": "banned_at"}}
                ]
            )

        # Lọc theo các thuộc tính khác
        if text:
            search = search.query("multi_match",
                                  query=text,
                                  fields=["name", "email", "phone"],
                                  fuzziness="AUTO"
                                  )
        if role:
            search = search.query(Term(role=role))
        if birthday:
            search = search.query(Term(birthday=birthday))
        if birthday_from:
            search = search.query(Range(birthday={'gte': birthday_from}))
        if birthday_to:
            search = search.query(Range(birthday={'lte': birthday_to}))
        if gender:
            search = search.query(Term(gender=gender))
        if created_from:
            search = search.query(Range(created_at={'gte': created_from}))
        if created_to:
            search = search.query(Range(created_at={'lte': created_to}))

        if paginate:
            search = search.sort({order_by: {"order": order_type}})
            search = search[skip: skip + page_size]

        response = search.execute()

        users = [user for user in response.hits]

        if paginate:
            return {
                'page_count': (response.hits.total.value - 1) // page_size + 1,
                'item_count': response.hits.total.value,
                'page_size': page_size,
                'page': page,
                'data': users
            }

        return users
