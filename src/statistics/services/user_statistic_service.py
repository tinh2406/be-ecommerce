from statistics.domains import UserStatisticsDomain


class UserStatisticService:

    @classmethod
    def get_user_statistics(cls, query_params):
        return UserStatisticsDomain.get_user_statistics(query_params)
