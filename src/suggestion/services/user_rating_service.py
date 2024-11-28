import random

import torch

from core.settings import BASE_DIR
from suggestion.utils import (
    get_20latest_rating_matrix,
    get_disinterest,
    get_hidden_user_rating_matrix,
    get_predicted_user_rating_matrix,
    get_real_user_rating_matrix,
    get_user_ids,
    masked_cosine_similarity_matrix,
    save_20latest_rating_matrix,
    save_disinterest,
    save_hidden_user_rating_matrix,
    save_real_user_rating_matrix,
    save_user_ids,
)

path = f"{BASE_DIR}/suggestion/data"

device = torch.device("mps" if torch.mps.is_available() else "cpu")


class UserRatingService:
    user_ids = get_user_ids(f"{path}/users/1ids.csv")
    sorted_products = []

    real_user_rating_matrix = get_real_user_rating_matrix(
        f"{path}/users/2real_rating.csv"
    )
    hidden_user_rating_matrix = get_hidden_user_rating_matrix(
        f"{path}/users/3hidden_rating.csv"
    )
    predicted_user_rating_matrix = get_predicted_user_rating_matrix(
        f"{path}/users/4predicted_rating.csv"
    )
    latest_rating_matrix = get_20latest_rating_matrix()
    disinterest = get_disinterest(f"{path}/users/6disinterest.csv")

    @classmethod
    def add_product(cls, new_product_idx: int):
        cls.sorted_products = torch.cat(
            [
                cls.sorted_products[:new_product_idx],
                torch.tensor([new_product_idx]),
                cls.sorted_products[new_product_idx:],
            ]
        )
        cls.real_user_rating_matrix = torch.cat(
            [
                cls.real_user_rating_matrix[:, :new_product_idx],
                torch.zeros(len(cls.user_ids), 1),
                cls.real_user_rating_matrix[:, new_product_idx:],
            ],
            dim=1,
        )
        cls.hidden_user_rating_matrix = torch.cat(
            [
                cls.hidden_user_rating_matrix[:, :new_product_idx],
                torch.zeros(len(cls.user_ids), 1),
                cls.hidden_user_rating_matrix[:, new_product_idx:],
            ],
            dim=1,
        )
        cls.disinterest = torch.cat(
            [
                cls.disinterest[:, :new_product_idx],
                torch.zeros(len(cls.user_ids), 1),
                cls.disinterest[:, new_product_idx:],
            ],
            dim=1,
        )
        cls.predicted_user_rating_matrix = torch.cat(
            [
                cls.predicted_user_rating_matrix[:, :new_product_idx],
                torch.zeros(len(cls.user_ids), 1),
                cls.predicted_user_rating_matrix[:, new_product_idx:],
            ],
            dim=1,
        )
        save_real_user_rating_matrix(cls.real_user_rating_matrix)
        save_hidden_user_rating_matrix(cls.hidden_user_rating_matrix)
        save_disinterest(cls.disinterest)

    @classmethod
    def add_user(cls, user_id: str):
        if user_id in cls.user_ids:
            raise ValueError("User already exists")

        cls.user_ids.append(user_id)
        cls.real_user_rating_matrix = torch.cat(
            [cls.real_user_rating_matrix, torch.zeros(1, len(cls.sorted_products))],
            dim=0,
        )
        cls.hidden_user_rating_matrix = torch.cat(
            [cls.hidden_user_rating_matrix, torch.zeros(1, len(cls.sorted_products))],
            dim=0,
        )
        cls.latest_rating_matrix = cls.latest_rating_matrix._append([[[-1], [-1]]])
        cls.disinterest = torch.cat(
            [cls.disinterest, torch.zeros(1, len(cls.sorted_products))], dim=0
        )

        save_user_ids(cls.user_ids)
        save_real_user_rating_matrix(cls.real_user_rating_matrix)
        save_hidden_user_rating_matrix(cls.hidden_user_rating_matrix)
        save_20latest_rating_matrix(cls.latest_rating_matrix)
        save_disinterest(cls.disinterest)
        return cls.user_ids

    @classmethod
    def add_real_user_rating(cls, idx_user: int, idx_product: int, rating: int):
        cls.real_user_rating_matrix[idx_user, idx_product] = rating
        cls.hidden_user_rating_matrix[idx_user, idx_product] = rating
        cls.add_latest_user_rating(idx_user, idx_product, rating)
        cls.remove_disinterest(idx_user, idx_product)

        save_real_user_rating_matrix(cls.real_user_rating_matrix)
        save_hidden_user_rating_matrix(cls.hidden_user_rating_matrix)

    @classmethod
    def remove_real_user_rating(cls, idx_user: int, idx_product: int):
        cls.real_user_rating_matrix[idx_user, idx_product] = 0
        cls.hidden_user_rating_matrix[idx_user, idx_product] = 0
        cls.remove_latest_user_rating(idx_user, idx_product)

        save_real_user_rating_matrix(cls.real_user_rating_matrix)
        save_hidden_user_rating_matrix(cls.hidden_user_rating_matrix)

    @classmethod
    def add_hidden_user_rating(cls, idx_user: int, idx_product: int, rating: int):
        current_rating = cls.hidden_user_rating_matrix[idx_user, idx_product]
        if current_rating == 0:
            cls.hidden_user_rating_matrix[idx_user, idx_product] = rating

        cls.add_latest_user_rating(idx_user, idx_product, rating)

        save_hidden_user_rating_matrix(cls.hidden_user_rating_matrix)

    @classmethod
    def add_disinterest(cls, idx_user: int, idx_product: int):

        current_rating = cls.hidden_user_rating_matrix[idx_user, idx_product]
        current_disinterest = cls.disinterest[idx_user, idx_product]

        cls.disinterest[idx_user, idx_product] = current_disinterest + 1
        if current_rating == 0 and current_disinterest > 10:
            cls.hidden_user_rating_matrix[idx_user, idx_product] = 1

        save_disinterest(cls.disinterest)

    @classmethod
    def remove_disinterest(cls, idx_user: int, idx_product: int):

        cls.disinterest[idx_user, idx_product] = 0
        save_disinterest(cls.disinterest)

    @classmethod
    def add_latest_user_rating(cls, idx_user: int, idx_product: int, rating: int):
        if rating == 2:
            row = cls.latest_rating_matrix[0][idx_user]
            if idx_product not in row:
                if len(row) < 20:
                    row.append(idx_product)
                else:
                    row.pop(0)
                    row.append(idx_product)
            else:
                row.remove(idx_product)
                row.append(idx_product)
            cls.latest_rating_matrix.loc[idx_user, 0] = row

        if rating == 1:
            row = cls.latest_rating_matrix[1][idx_user]
            if idx_product not in row:
                if len(row) < 20:
                    row.append(idx_product)
                else:
                    row.pop(0)
                    row.append(idx_product)
            else:
                row.remove(idx_product)
                row.append(idx_product)

            cls.latest_rating_matrix.loc[idx_user, 1] = row

        save_20latest_rating_matrix(cls.latest_rating_matrix)

    @classmethod
    def remove_latest_user_rating(cls, idx_user: int, idx_product: int):
        row = cls.latest_rating_matrix[0][idx_user]
        if idx_product in row:
            row.remove(idx_product)
            cls.latest_rating_matrix.loc[idx_user, 0] = row

        row = cls.latest_rating_matrix[1][idx_user]
        if idx_product in row:
            row.remove(idx_product)
            cls.latest_rating_matrix.loc[idx_user, 1] = row

        save_20latest_rating_matrix(cls.latest_rating_matrix)

    @classmethod
    def find_similar_base_latest_rating(cls, latest_like, latest_dislike):
        user_ratings = torch.zeros(1, len(cls.sorted_products))
        for i in latest_like:
            user_ratings[0, i] = 2
        for i in latest_dislike:
            user_ratings[0, i] = 1

        similarity_matrix = masked_cosine_similarity_matrix(
            cls.hidden_user_rating_matrix.float().to(device),
            user_ratings.to(device),
            min_common=len(latest_like) + len(latest_dislike),
        )

        similar_users = torch.argsort(
            similarity_matrix.squeeze(), descending=True
        ).tolist()
        similarity = torch.sort(
            similarity_matrix.squeeze(), descending=True
        ).values.tolist()
        similar_users = [
            [user, sim] for user, sim in zip(similar_users, similarity) if sim > 0.8
        ][:3]

        return similar_users

    @classmethod
    def find_similar_user(cls, idx_user: int):
        return cls.find_similar_base_latest_rating(
            cls.latest_rating_matrix[0][idx_user], cls.latest_rating_matrix[1][idx_user]
        )

    @classmethod
    def get_predict_user_rating(cls, similar_users, idx_user=None):

        if len(similar_users) == 0:
            return []

        near_user = similar_users[0]
        near_idx_user = near_user[0]
        similarity = near_user[1]
        predict_ratings = cls.predicted_user_rating_matrix[near_idx_user] * similarity

        for near_user in similar_users[1:]:
            near_idx_user = near_user[0]
            similarity = near_user[1]
            predict_ratings += (
                cls.predicted_user_rating_matrix[near_idx_user] * similarity
            )

        if idx_user:
            top_10_rated = torch.argsort(predict_ratings, descending=True)[:10].tolist()
            top_10_rated = [cls.sorted_products[i] for i in top_10_rated]

            top_10_unrated = torch.argsort(predict_ratings, descending=True).tolist()
            top_10_unrated = [
                cls.sorted_products[i]
                for i in top_10_unrated
                if cls.hidden_user_rating_matrix[idx_user, i] == 0
            ][:10]

            return top_10_rated + top_10_unrated

        return torch.argsort(predict_ratings, descending=True).tolist()[:20]

    @classmethod
    def get_highest_product_rating(cls):
        mean = torch.mean(cls.hidden_user_rating_matrix, dtype=float, dim=0)
        if max(mean) < 0.1:
            return list(
                {random.randint(0, len(cls.sorted_products) - 1) for _ in range(20)}
            )
        highest_ratings = torch.argsort(
            mean,
            descending=True,
        ).tolist()[:20]

        return highest_ratings
