import threading

import torch

from suggestion.domains import ProductSimilarityDomain, UserRatingDomain


class RatingService:
    @classmethod
    def real_rating(cls, user_id, product_id, rating):

        user_id = str(user_id).replace("-", "")
        product_id = str(product_id).replace("-", "")

        idx_user = UserRatingDomain.user_ids.index(user_id)
        idx_product = ProductSimilarityDomain.ids.index(product_id)

        idx_product = torch.where(
            ProductSimilarityDomain.sorted_products == idx_product
        )[0].item()

        if rating == 0:
            thread = threading.Thread(
                target=UserRatingDomain.remove_real_user_rating,
                args=(idx_user, idx_product),
            )
            thread.start()

        else:
            thread = threading.Thread(
                target=UserRatingDomain.add_real_user_rating,
                args=(idx_user, idx_product, rating),
            )
            thread.start()

    @classmethod
    def hidden_rating(cls, user_id, product_id, rating):

        user_id = str(user_id).replace("-", "")
        product_id = str(product_id).replace("-", "")

        idx_user = UserRatingDomain.user_ids.index(user_id)
        idx_product = ProductSimilarityDomain.ids.index(product_id)

        idx_product = torch.where(
            ProductSimilarityDomain.sorted_products == idx_product
        )[0].item()

        thread = threading.Thread(
            target=UserRatingDomain.add_hidden_user_rating,
            args=(idx_user, idx_product, rating),
        )
        thread.start()

    @classmethod
    def disinterest_rating(cls, user_id, product_id):

        user_id = str(user_id).replace("-", "")
        product_id = str(product_id).replace("-", "")

        idx_user = UserRatingDomain.user_ids.index(user_id)
        idx_product = ProductSimilarityDomain.ids.index(product_id)
        idx_product = torch.where(
            ProductSimilarityDomain.sorted_products == idx_product
        )[0].item()

        thread = threading.Thread(
            target=UserRatingDomain.add_disinterest,
            args=(
                idx_user,
                idx_product,
            ),
        )
        thread.start()
