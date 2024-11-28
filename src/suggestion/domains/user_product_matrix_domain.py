from suggestion.services import (
    EmbeddingService,
    ProductSimilarityService,
    UserRatingService,
)
from suggestion.services.predict_user_rating_service import Rating
from suggestion.utils import save_predicted_user_rating_matrix


class UserProductMatrixDomain:

    UserRatingService.sorted_products = ProductSimilarityService.sorted_products

    @classmethod
    def add_new_products(cls, products: dict):
        new_id, new_embedding = EmbeddingService.embedding(products)
        ProductSimilarityService.add_new_product(new_id, new_embedding)

    @classmethod
    def predict_rating_for_user(cls):
        n_users = len(UserRatingService.user_ids)
        tr = UserRatingService.hidden_user_rating_matrix.T
        tm = tr != 0
        model = Rating(n_users, 2, 10, 500, 0.01, 0.01)
        model.train_and_validate(100, tr, tr, tm, tm)
        predict = model.predict(tr).cpu()
        save_predicted_user_rating_matrix(predict.T)
        UserRatingService.predicted_user_rating_matrix = predict.T
