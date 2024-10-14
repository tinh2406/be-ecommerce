from django.contrib.auth.base_user import BaseUserManager

from core.managers import BaseCacheManager


class UserManager(BaseUserManager, BaseCacheManager):
    def create_user(
        self,
        email,
        password,
        name,
    ):
        if not email:
            raise ValueError("User must have an email address")
        if not password:
            raise ValueError("User must have an password")
        user = self.model(email=self.normalize_email(email))
        user.name = name
        user.set_password(password)

        user.save(using=self._db)
        return user
