import numpy as np

from .product_similarity_service import ProductSimilarityService
from .user_rating_service import UserRatingService


class SuggestionsService:

    @classmethod
    def get_suggestion(
        cls,
        user_id: str | None = None,
        latest_ratings: list | None = None,
        product_id: str | None = None,
    ) -> list[str]:
        products = set()

        idx_product = None
        if product_id:
            idx_product = ProductSimilarityService.ids.index(
                product_id.replace("-", "")
            )

        if user_id:
            idx_user = UserRatingService.user_ids.index(str(user_id).replace("-", ""))
            nearest_products = UserRatingService.latest_rating_matrix[0][idx_user]
            predict_products = UserRatingService.get_predict_user_rating(
                UserRatingService.find_similar_user(idx_user)
            )
            _products = nearest_products + predict_products

            if idx_product:
                _products = _products[:2]
                nearest_products = (
                    ProductSimilarityService.sorted_matrix[idx_product][:20]
                    .int()
                    .cpu()
                    .numpy()
                    .tolist()
                )

                for idx in nearest_products:
                    similar_products = (
                        ProductSimilarityService.sorted_matrix[idx][:15]
                        .int()
                        .cpu()
                        .numpy()
                        .tolist()
                    )
                    for similar_product in similar_products:
                        products.add(ProductSimilarityService.ids[similar_product])

            for i in _products:
                idx = ProductSimilarityService.sorted_products[i]
                similar_products = (
                    ProductSimilarityService.sorted_matrix[idx][:15]
                    .int()
                    .cpu()
                    .numpy()
                    .tolist()
                )
                for similar_product in similar_products:
                    if (
                        similar_product not in products
                        and UserRatingService.disinterest[idx_user][similar_product]
                        <= 10
                    ):
                        products.add(ProductSimilarityService.ids[similar_product])

            if len(products) > 50:
                return list(products)

        if latest_ratings:
            latest_ratings = [
                [
                    ProductSimilarityService.sorted_products.cpu()
                    .numpy()
                    .tolist()
                    .index(ProductSimilarityService.ids.index(product_id))
                    for product_id in latest_rating
                ]
                for latest_rating in latest_ratings
            ]
            nearest_products = latest_ratings[0]
            predict_products = UserRatingService.get_predict_user_rating(
                UserRatingService.find_similar_base_latest_rating(
                    latest_ratings[0], latest_ratings[1]
                )
            )
            _products = nearest_products + predict_products

            if idx_product:
                _products = _products[:2]
                nearest_products = (
                    ProductSimilarityService.sorted_matrix[idx_product][:20]
                    .int()
                    .cpu()
                    .numpy()
                    .tolist()
                )

                for idx in nearest_products:
                    similar_products = (
                        ProductSimilarityService.sorted_matrix[idx][:15]
                        .int()
                        .cpu()
                        .numpy()
                        .tolist()
                    )
                    for similar_product in similar_products:
                        products.add(ProductSimilarityService.ids[similar_product])

            for i in _products:
                idx = ProductSimilarityService.sorted_products[i]
                similar_products = (
                    ProductSimilarityService.sorted_matrix[idx][:15]
                    .int()
                    .cpu()
                    .numpy()
                    .tolist()
                )
                for similar_product in similar_products:
                    products.add(ProductSimilarityService.ids[similar_product])

            if len(products) > 100:
                return list(products)

        highest_rating_products = UserRatingService.get_highest_product_rating()
        for i in highest_rating_products:
            idx = ProductSimilarityService.sorted_products[i]
            similar_products = (
                ProductSimilarityService.sorted_matrix[idx][:10]
                .int()
                .cpu()
                .numpy()
                .tolist()
            )
            for similar_product in similar_products:
                products.add(ProductSimilarityService.ids[similar_product])
        list_products = list(products)
        np.random.shuffle(list_products)
        return list_products
