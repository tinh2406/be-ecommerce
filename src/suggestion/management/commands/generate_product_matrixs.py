import torch
from django.core.management import BaseCommand
from django.db import connection

from src.suggestion.domains.embedding_domain import EmbeddingDomain
from src.suggestion.domains.product_similarity_domain import (
    save_embeddings,
    save_ids,
    save_similarity_matrix,
    save_sorted_matrix,
    save_sorted_products,
)
from suggestion.utils import (
    create_similarity_matrix,
    create_sorted_similarity_matrix,
    create_sorted_similarity_products,
)

device = torch.device("mps" if torch.mps.is_available() else "cpu")


def create_embeddings(products: list[dict]) -> tuple[list[str], torch.Tensor]:
    ids, embeddings = EmbeddingDomain.embedding(products)
    embeddings = torch.tensor(embeddings).float().to(device)
    return ids, embeddings


class Command(BaseCommand):
    help = "Create product matrix's"

    def handle(self, *args, **options):

        query = """select p.id,p.name,p.price,p.hot_price,p.description,c.name category,ats.attributes,
            group_concat(avs.attribute_values separator ', ') variants
            from products p left join categories c on p.category_id = c.id
            left join (
                select p.id, group_concat( pav.value SEPARATOR ', ') attribute_values
                    from products p
                        left join product_attributes pa on p.id = pa.product_id
                        left join product_attribute_values pav on pa.id = pav.attribute_id
                    where p.deleted_at is null
                    group by p.id, pa.name
            ) avs on p.id=avs.id
            left join (
                select id,group_concat(sub.name separator ', ') attributes  from (
                    select p.id, pa.name from products p
                        left join product_attributes pa on p.id = pa.product_id
                        left join ecommerce.product_attribute_values pav on pa.id = pav.attribute_id
                    where p.deleted_at is null
                    group by p.id, pa.name
                ) sub group by id
            ) ats on ats.id = p.id
            where p.deleted_at is null
            group by p.id"""

        products = []
        with connection.cursor() as cursor:
            cursor.execute(query)
            columns = [col[0] for col in cursor.description]
            for row in cursor.fetchall():
                products.append(dict(zip(columns, row)))

        ids, embeddings = create_embeddings(products)
        similarity_matrix = create_similarity_matrix(embeddings)
        sorted_products = create_sorted_similarity_products(similarity_matrix)
        sorted_matrix = create_sorted_similarity_matrix(similarity_matrix)

        save_ids(ids)
        save_embeddings(embeddings)
        save_similarity_matrix(similarity_matrix)
        save_sorted_products(sorted_products)
        save_sorted_matrix(sorted_matrix)

        self.stdout.write(self.style.SUCCESS("Product matrix's created successfully"))
