from statistics.domains import ProductStatisticsDomain


class ProductStatisticService:

    @classmethod
    def get_product_statistics(cls, query_params):
        return ProductStatisticsDomain.get_product_statistics(query_params)
