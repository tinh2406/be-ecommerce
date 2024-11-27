from django.contrib.auth.models import AnonymousUser
from rest_framework.permissions import BasePermission

from users.constants import Roles


class IsAdminPermission(BasePermission):
    """
    Allows access only to admin users.
    """

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user and not isinstance(user, AnonymousUser) and user.role == Roles.ADMIN
        )
