from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied

from users.constants import Roles


class Permission:

    @staticmethod
    def check_staff_permission(request):
        user = request.user
        if not user or isinstance(user, AnonymousUser) or user.role == Roles.CUSTOMER:
            raise PermissionDenied("You cannot do this action")

    @staticmethod
    def check_admin_permission(request):
        user = request.user

        if not user or isinstance(user, AnonymousUser) or user.role != Roles.ADMIN:
            raise PermissionDenied("You cannot do this action")
