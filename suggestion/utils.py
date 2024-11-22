import torch


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
