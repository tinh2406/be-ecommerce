from core.services import BaseDeleteService, BaseRetrieveService
from users.domains import ESUserDomain, JWTDomain, ProfileDomain, UserDomain
from users.serializers import UserSerializer


class UserService(BaseRetrieveService, BaseDeleteService):

    main_domain = UserDomain

    @classmethod
    def update(cls, user, update_data):
        UserDomain.update(user, update_data)
        ProfileDomain.update(user.profile, update_data)
        ESUserDomain.index.delay(UserSerializer(user).data)
        return user

    @classmethod
    def update_email(cls, token, new_email) -> bool:
        decoded_data = JWTDomain.confirm_verify_token(token)

        if UserDomain.update_email(decoded_data, new_email):
            ESUserDomain.index.delay(UserSerializer(decoded_data).data)
            return True
        return False

    @classmethod
    def update_password(cls, user, old_password, new_password):
        return UserDomain.update_password(user, old_password, new_password)

    @classmethod
    def on_delete_success(cls, pk):
        ESUserDomain.soft_delete.delay(pk)

    @classmethod
    def on_restore_success(cls, pk):
        ESUserDomain.restore.delay(pk)

    @classmethod
    def ban(cls, pk) -> bool:
        if UserDomain.ban(pk):
            ESUserDomain.index.delay(UserSerializer(UserDomain.get(pk)).data)
            return True
        return False

    @classmethod
    def unban(cls, pk) -> bool:
        if UserDomain.unban(pk):
            ESUserDomain.index.delay(UserSerializer(UserDomain.get(pk)).data)
            return True
        return False

    @classmethod
    def update_role(cls, executor, executed_pk, role) -> bool:
        if UserDomain.update_role(executor, executed_pk, role):
            ESUserDomain.index.delay(UserSerializer(UserDomain.get(executed_pk)).data)
            return True
        return False

    @classmethod
    def search_user(cls, query_params):
        return ESUserDomain.search(query_params)
