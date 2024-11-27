from core.domains import BaseDeleteDomain, BaseRetrieveDomain
from users.serializers import UserSerializer
from users.services import ESUserService, JWTService, ProfileService, UserService


class UserDomain(BaseRetrieveDomain, BaseDeleteDomain):

    main_service = UserService

    @classmethod
    def update(cls, user, update_data):
        UserService.update(user, update_data)
        ProfileService.update(user.profile, update_data)
        ESUserService.index.delay(UserSerializer(user).data)
        return user

    @classmethod
    def update_email(cls, token, new_email) -> bool:
        decoded_data = JWTService.confirm_verify_token(token)

        if UserService.update_email(decoded_data, new_email):
            ESUserService.index.delay(UserSerializer(decoded_data).data)
            return True
        return False

    @classmethod
    def update_password(cls, user, old_password, new_password):
        return UserService.update_password(user, old_password, new_password)

    @classmethod
    def on_delete_success(cls, pk):
        ESUserService.soft_delete.delay(pk)

    @classmethod
    def on_restore_success(cls, pk):
        ESUserService.restore.delay(pk)

    @classmethod
    def ban(cls, pk) -> bool:
        if UserService.ban(pk):
            ESUserService.index.delay(UserSerializer(UserService.get(pk)).data)
            return True
        return False

    @classmethod
    def unban(cls, pk) -> bool:
        if UserService.unban(pk):
            ESUserService.index.delay(UserSerializer(UserService.get(pk)).data)
            return True
        return False

    @classmethod
    def update_role(cls, executor, executed_pk, role) -> bool:
        if UserService.update_role(executor, executed_pk, role):
            ESUserService.index.delay(UserSerializer(UserService.get(executed_pk)).data)
            return True
        return False

    @classmethod
    def search_user(cls, query_params):
        return ESUserService.search(query_params)
