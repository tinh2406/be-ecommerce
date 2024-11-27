import pandas as pd
import torch

from core.settings import BASE_DIR

path = f"{BASE_DIR}/suggestion/data"
device = torch.device("mps" if torch.mps.is_available() else "cpu")


def masked_cosine_similarity_matrix(
    vecs1: torch.tensor, vecs2: torch.tensor, min_common=5
):
    """
    Tính cosine similarity cho từng cặp hàng giữa hai ma trận, bỏ qua giá trị 0.
    Args:
        vecs1: Tensor (N x D), ma trận 1.
        vecs2: Tensor (M x D), ma trận 2.
        min_common: Số lượng phần tử tối thiểu không phải 0 để tính similarity.
    Returns:
        Tensor (N x M): Ma trận cosine similarity.
    """
    # Mặt nạ (mask) để xác định các giá trị hợp lệ (khác 0)
    mask1 = vecs1 != 0  # Kích thước (N x D)
    mask2 = vecs2 != 0  # Kích thước (M x D)

    # Tích hợp mask để chỉ giữ các giá trị chung
    common_mask = mask1.unsqueeze(1) & mask2.unsqueeze(0)  # Kích thước (N x M x D)

    # Đếm số lượng phần tử chung cho mỗi cặp vector
    num_common = common_mask.sum(dim=2)  # Kích thước (N x M)

    # Áp dụng điều kiện số lượng phần tử chung >= min_common
    valid_mask = num_common >= min_common

    # Áp dụng mask vào vecs1 và vecs2
    vecs1_masked = (
        vecs1.unsqueeze(1).expand(-1, vecs2.size(0), -1) * common_mask
    )  # Kích thước (N x M x D)
    vecs2_masked = (
        vecs2.unsqueeze(0).expand(vecs1.size(0), -1, -1) * common_mask
    )  # Kích thước (N x M x D)

    vecs1_masked -= 1
    vecs2_masked -= 1

    # Tính dot product
    dot_products = (vecs1_masked * vecs2_masked).sum(dim=2)  # Kích thước (N x M)

    # Tính norm
    norm_vecs1 = torch.sqrt((vecs1_masked**2).sum(dim=2))  # Kích thước (N x M)
    norm_vecs2 = torch.sqrt((vecs2_masked**2).sum(dim=2))  # Kích thước (N x M)

    # Tránh chia cho 0
    norm_product = norm_vecs1 * norm_vecs2
    cosine_similarity = torch.zeros_like(dot_products)
    cosine_similarity[valid_mask] = dot_products[valid_mask] / norm_product[valid_mask]

    return cosine_similarity


def create_similarity_matrix(embeddings: torch.Tensor) -> torch.Tensor:
    embeddings = torch.nn.functional.normalize(embeddings, p=2, dim=1)

    similarity_matrix = torch.mm(embeddings, embeddings.T)

    return similarity_matrix


def create_sorted_similarity_products(similarity_matrix: torch.Tensor) -> torch.Tensor:
    n = len(similarity_matrix)
    saved = {0}
    result = [0]

    similarity_matrix = similarity_matrix.clone()

    while len(result) < n:
        last = result[-1]

        similarity_matrix[last, list(saved)] = -float("inf")

        max_id = torch.argmax(similarity_matrix[last]).item()

        result.append(max_id)
        saved.add(max_id)

    return torch.tensor(result)


def create_sorted_similarity_matrix(similarity_matrix: torch.Tensor) -> torch.Tensor:
    new_matrix = []
    similarity_matrix = similarity_matrix.clone()
    n = len(similarity_matrix)

    for idx in range(n):
        row = similarity_matrix[idx]

        sorted_indices = torch.argsort(row, descending=True).tolist()

        new_matrix.append(sorted_indices)

    return torch.tensor(new_matrix)


def get_user_ids(file_path: str) -> list[str]:
    ids = pd.read_csv(file_path, header=None)
    return ids.to_numpy().flatten().tolist()


def save_user_ids(user_ids: list[str]):
    user_ids_df = pd.DataFrame(user_ids)
    user_ids_df.to_csv(f"{path}/users/1ids.csv", index=False, header=False)


def get_real_user_rating_matrix(file_path: str) -> torch.Tensor:
    matrix = pd.read_csv(file_path, header=None)
    matrix = torch.tensor(matrix.values)
    return matrix


def save_real_user_rating_matrix(user_rating_matrix: torch.Tensor):
    user_rating_matrix = pd.DataFrame(user_rating_matrix.numpy())
    user_rating_matrix.to_csv(
        f"{path}/users/2real_rating.csv", index=False, header=False
    )


def get_hidden_user_rating_matrix(file_path: str) -> torch.Tensor:
    matrix = pd.read_csv(file_path, header=None)
    matrix = torch.tensor(matrix.values)
    return matrix


def save_hidden_user_rating_matrix(user_rating_matrix: torch.Tensor):
    user_rating_matrix = pd.DataFrame(user_rating_matrix.numpy())
    user_rating_matrix.to_csv(
        f"{path}/users/3hidden_rating.csv", index=False, header=False
    )


def get_predicted_user_rating_matrix(file_path: str) -> torch.Tensor:
    matrix = pd.read_csv(file_path, header=None)
    matrix = torch.tensor(matrix.values)
    return matrix


def save_predicted_user_rating_matrix(user_rating_matrix: torch.Tensor):
    user_rating_matrix = pd.DataFrame(user_rating_matrix.numpy())
    user_rating_matrix.to_csv(
        f"{path}/users/4predicted_rating.csv", index=False, header=False
    )


def get_20latest_rating_matrix() -> pd.DataFrame:
    like = pd.read_csv(f"{path}/users/5_20latest_like_rating.csv", header=None)
    dislike = pd.read_csv(f"{path}/users/5_20latest_dislike_rating.csv", header=None)

    matrix = []
    for i in range(len(like)):
        _like = [int(i) for i in like.iloc[i].tolist() if not pd.isna(i) and i != -1]
        _dislike = [
            int(i) for i in dislike.iloc[i].tolist() if not pd.isna(i) and i != -1
        ]
        matrix.append([_like, _dislike])

    return pd.DataFrame(matrix)


def save_20latest_rating_matrix(user_rating_matrix: pd.DataFrame):
    like = []
    dislike = []
    for i in range(len(user_rating_matrix)):
        _like = user_rating_matrix.iloc[i][0]
        _dislike = user_rating_matrix.iloc[i][1]
        if len(_like) < 20:
            _like = _like + [-1] * (20 - len(_like))
        if len(_dislike) < 20:
            _dislike = _dislike + [-1] * (20 - len(_dislike))
        like.append(_like)
        dislike.append(_dislike)

    pd.DataFrame(like).to_csv(
        f"{path}/users/5_20latest_like_rating.csv", index=False, header=False
    )
    pd.DataFrame(dislike).to_csv(
        f"{path}/users/5_20latest_dislike_rating.csv", index=False, header=False
    )


def get_disinterest(file_path: str) -> torch.Tensor:
    disinterest = pd.read_csv(file_path, header=None)
    disinterest = torch.tensor(disinterest.values)
    return disinterest


def save_disinterest(disinterest: torch.Tensor):
    disinterest = pd.DataFrame(disinterest.numpy())
    disinterest.to_csv(f"{path}/users/6disinterest.csv", index=False, header=False)


def get_old_ids(file_path: str) -> list[str]:
    ids = pd.read_csv(file_path, header=None)
    ids = ids.to_numpy().flatten().tolist()
    return ids


def get_old_embeddings(file_path: str) -> torch.Tensor:
    embeddings = pd.read_csv(file_path, header=None)
    embeddings = torch.tensor(embeddings.to_numpy()).float().to(device)
    return embeddings


def get_old_similarity_matrix(file_path: str) -> torch.Tensor:
    matrix = pd.read_csv(file_path, header=None)
    matrix = torch.tensor(matrix.to_numpy()).float().to(device)
    return matrix


def get_old_sorted_matrix(file_path: str) -> torch.Tensor:
    matrix = pd.read_csv(file_path, header=None)
    matrix = torch.tensor(matrix.to_numpy()).int().to(device)
    return matrix


def get_old_sorted_products(file_path: str) -> torch.Tensor:
    products = pd.read_csv(file_path, header=None)
    products = torch.tensor(products.to_numpy().flatten()).int().to(device)
    return products
