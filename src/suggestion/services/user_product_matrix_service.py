from suggestion.domains import (
    EmbeddingDomain,
    ProductSimilarityDomain,
    UserRatingDomain,
)
from src.suggestion.domains.predict_user_rating_domain import Rating
from suggestion.utils import save_predicted_user_rating_matrix


class UserProductMatrixService:

    UserRatingDomain.sorted_products = ProductSimilarityDomain.sorted_products

    @classmethod
    def add_new_products(cls, products: dict):
        new_id, new_embedding = EmbeddingDomain.embedding(products)
        ProductSimilarityDomain.add_new_product(new_id, new_embedding)

    @classmethod
    def predict_rating_for_user(cls):
        n_users = len(UserRatingDomain.user_ids)
        tr = UserRatingDomain.hidden_user_rating_matrix.T
        tm = tr != 0
        model = Rating(n_users, 2, 10, 500, 0.01, 0.01)
        model.train_and_validate(100, tr, tr, tm, tm)
        predict = model.predict(tr).cpu()
        save_predicted_user_rating_matrix(predict.T)
        UserRatingDomain.predicted_user_rating_matrix = predict.T
