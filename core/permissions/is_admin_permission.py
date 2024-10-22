from rest_framework.permissions import BasePermission

from users.constants import Roles


class IsAdminPermission(BasePermission):
    """
    Allows access only to admin users.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.role == Roles.ADMIN)
