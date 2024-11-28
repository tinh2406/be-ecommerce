import threading

import torch

from suggestion.services import ProductSimilarityService, UserRatingService


class RatingDomain:
    @classmethod
    def real_rating(cls, user_id, product_id, rating):

        user_id = str(user_id).replace("-", "")
        product_id = str(product_id).replace("-", "")

        idx_user = UserRatingService.user_ids.index(user_id)
        idx_product = ProductSimilarityService.ids.index(product_id)

        idx_product = torch.where(
            ProductSimilarityService.sorted_products == idx_product
        )[0].item()

        if rating == 0:
            thread = threading.Thread(
                target=UserRatingService.remove_real_user_rating,
                args=(idx_user, idx_product),
            )
            thread.start()

        else:
            thread = threading.Thread(
                target=UserRatingService.add_real_user_rating,
                args=(idx_user, idx_product, rating),
            )
            thread.start()

    @classmethod
    def hidden_rating(cls, user_id, product_id, rating):

        user_id = str(user_id).replace("-", "")
        product_id = str(product_id).replace("-", "")

        idx_user = UserRatingService.user_ids.index(user_id)
        idx_product = ProductSimilarityService.ids.index(product_id)

        idx_product = torch.where(
            ProductSimilarityService.sorted_products == idx_product
        )[0].item()

        thread = threading.Thread(
            target=UserRatingService.add_hidden_user_rating,
            args=(idx_user, idx_product, rating),
        )
        thread.start()

    @classmethod
    def disinterest_rating(cls, user_id, product_id):

        user_id = str(user_id).replace("-", "")
        product_id = str(product_id).replace("-", "")

        idx_user = UserRatingService.user_ids.index(user_id)
        idx_product = ProductSimilarityService.ids.index(product_id)
        idx_product = torch.where(
            ProductSimilarityService.sorted_products == idx_product
        )[0].item()

        thread = threading.Thread(
            target=UserRatingService.add_disinterest,
            args=(
                idx_user,
                idx_product,
            ),
        )
        thread.start()
