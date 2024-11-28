import torch

from core.settings import BASE_DIR

from ..utils import (
    create_sorted_similarity_matrix,
    create_sorted_similarity_products,
    get_old_embeddings,
    get_old_ids,
    get_old_similarity_matrix,
    get_old_sorted_matrix,
    get_old_sorted_products,
    save_embeddings,
    save_ids,
    save_similarity_matrix,
    save_sorted_matrix,
    save_sorted_products,
)

path = f"{BASE_DIR}/suggestion/data"

device = torch.device("mps" if torch.mps.is_available() else "cpu")


class ProductSimilarityService:
    ids = get_old_ids(f"{path}/products/1ids.csv")
    embeddings = get_old_embeddings(f"{path}/products/2embeddings.csv")
    similarity_matrix = get_old_similarity_matrix(
        f"{path}/products/3similarity_matrix.csv"
    )
    sorted_products = get_old_sorted_products(f"{path}/products/4sorted_products.csv")
    sorted_matrix = get_old_sorted_matrix(f"{path}/products/5sorted_matrix.csv")

    @classmethod
    def add_new_product(cls, new_id, new_embedding):

        if new_id in cls.ids:
            raise ValueError("Product already exists")

        cls.ids.append(new_id)

        new_embedding = torch.tensor([new_embedding]).float().to(device)
        cls.embeddings = torch.cat([cls.embeddings, new_embedding], dim=0)

        new_similarity_vector = cls._calculate_similarity_vector(new_embedding)
        cls.similarity_matrix = cls._update_similarity_matrix(new_similarity_vector)

        # Cập nhật sorted products và matrix
        new_sorted_products = create_sorted_similarity_products(cls.similarity_matrix)
        new_sorted_matrix = create_sorted_similarity_matrix(cls.similarity_matrix)

        # Lưu dữ liệu
        cls.sorted_products = new_sorted_products
        cls.sorted_matrix = new_sorted_matrix

        cls.save_all()

    @classmethod
    def remove_product(cls, product_id):
        try:
            idx = cls.ids.index(product_id)
        except ValueError:
            raise ValueError("Product not found")

        cls.ids = [cls.ids[:idx] + cls.ids[idx + 1 :]]
        cls.embeddings = torch.cat([cls.embeddings[:idx], cls.embeddings[idx + 1 :]])

        # Loại bỏ hàng và cột tương ứng khỏi cls.similarity_matrix
        cls.similarity_matrix = torch.cat(
            [cls.similarity_matrix[:idx], cls.similarity_matrix[idx + 1 :]], dim=0
        )
        cls.similarity_matrix = torch.cat(
            [cls.similarity_matrix[:, :idx], cls.similarity_matrix[:, idx + 1 :]], dim=1
        )

        # Tạo lại danh sách sản phẩm và ma trận được sắp xếp
        new_sorted_products = create_sorted_similarity_products(cls.similarity_matrix)
        new_sorted_matrix = create_sorted_similarity_matrix(cls.similarity_matrix)

        cls.sorted_products = new_sorted_products
        cls.sorted_matrix = new_sorted_matrix

        cls.save_all()

    @classmethod
    def _calculate_similarity_vector(cls, new_embedding: torch.Tensor) -> torch.Tensor:
        similarity_vector = torch.nn.functional.cosine_similarity(
            new_embedding, cls.embeddings, dim=1
        )
        return similarity_vector

    @classmethod
    def _update_similarity_matrix(
        cls, new_similarity_vector: torch.Tensor
    ) -> torch.Tensor:

        new_similarity_vector = new_similarity_vector.to(device=device)

        updated_matrix = torch.cat(
            [cls.similarity_matrix, new_similarity_vector[:-1].unsqueeze(0)], dim=0
        )

        new_column = new_similarity_vector.unsqueeze(1)
        updated_matrix = torch.cat([updated_matrix, new_column], dim=1)

        return updated_matrix

    @classmethod
    def save_all(cls):
        """Lưu tất cả các thuộc tính vào bộ nhớ hoặc file."""
        save_ids(cls.ids)
        save_embeddings(cls.embeddings)
        save_similarity_matrix(cls.similarity_matrix)
        save_sorted_matrix(cls.sorted_matrix)
        save_sorted_products(cls.sorted_products)
