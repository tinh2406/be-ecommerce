from django.core.exceptions import PermissionDenied


class Permission():

    @staticmethod
    def check_staff_permission(request):
        user = request.user
        if not user or user.role == 3:
            raise PermissionDenied("You cannot do this action")

    @staticmethod
    def check_admin_permission(request):
        user = request.user
        if not user or user.role != 1:
            raise PermissionDenied("You cannot do this action")