import pickle
import uuid

from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import PermissionsMixin
from django.db.models import UUIDField, EmailField, CharField, DateTimeField, IntegerField

from core.common import BaseTimeModel
from users.constants import Roles
from users.managers import UserManager


class User(AbstractBaseUser, PermissionsMixin, BaseTimeModel):
    id = UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    email = EmailField(unique=True)
    name = CharField(max_length=255)

    role = IntegerField(choices=Roles.CHOICES, default=Roles.CUSTOMER)

    banned_at = DateTimeField(null=True, blank=True)

    USERNAME_FIELD = 'email'
    key = 'user_'
    cache_fields = ['id', 'email']

    objects = UserManager()

    class Meta:
        db_table = 'users'

    def set_password(self, raw_password):
        self.password = make_password(raw_password, salt=settings.SECRET_KEY)
        self._password = raw_password

    @property
    def role_name(self):
        return Roles.DICT.get(self.role)

