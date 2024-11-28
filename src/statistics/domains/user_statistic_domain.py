from statistics.services import UserStatisticsService


class UserStatisticDomain:

    @classmethod
    def get_user_statistics(cls, query_params):
        return UserStatisticsService.get_user_statistics(query_params)
