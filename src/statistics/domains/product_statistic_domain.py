from statistics.services import ProductStatisticsService


class ProductStatisticDomain:

    @classmethod
    def get_product_statistics(cls, query_params):
        return ProductStatisticsService.get_product_statistics(query_params)
