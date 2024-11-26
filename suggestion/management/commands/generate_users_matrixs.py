import pandas as pd
import torch
from django.core.management import BaseCommand
from django.db import connection

from core.settings import BASE_DIR
from suggestion.services.product_similarity_service import get_old_sorted_products
from suggestion.utils import (
    save_20latest_rating_matrix,
    save_disinterest,
    save_hidden_user_rating_matrix,
    save_predicted_user_rating_matrix,
    save_real_user_rating_matrix,
    save_user_ids,
)

path = f"{BASE_DIR}/suggestion/data"


class Command(BaseCommand):
    help = "Generate user matrix's"

    def handle(self, *args, **options):
        query = """select id from users"""

        users = []
        with connection.cursor() as cursor:
            cursor.execute(query)
            columns = [col[0] for col in cursor.description]
            for row in cursor.fetchall():
                users.append(dict(zip(columns, row)))

        sorted_products = get_old_sorted_products(
            f"{path}/products/4sorted_products.csv"
        )

        user_ids = [user["id"] for user in users]
        real_ratings = torch.zeros(len(user_ids), len(sorted_products))
        hidden_ratings = torch.zeros(len(user_ids), len(sorted_products))
        latest_ratings = pd.DataFrame(
            ([[-1] for _ in range(len(user_ids))], [[-1] for _ in range(len(user_ids))])
        )
        predicts = torch.zeros(len(user_ids), len(sorted_products))
        disinterest = torch.zeros(len(user_ids), len(sorted_products))

        save_user_ids(user_ids)
        save_real_user_rating_matrix(real_ratings)
        save_hidden_user_rating_matrix(hidden_ratings)
        save_20latest_rating_matrix(latest_ratings)
        save_predicted_user_rating_matrix(predicts)
        save_disinterest(disinterest)

        self.stdout.write(self.style.SUCCESS("User matrix's generated successfully"))
