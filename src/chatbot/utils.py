import json

from core.settings import BASE_DIR

CATEGORIES_SOURCE_PATH = f"{BASE_DIR}/suggestion/data/categories.json"
PRODUCTS_SOURCE_PATH = f"{BASE_DIR}/suggestion/data/products.json"


def retrieve_categories():
    """
    [{
    "id": "004800e666bb4d7eb2d7ae0d6251f42e",
    "name": "Mỹ thuật - Kiến trúc Việt Nam"
    },...]
    """
    with open(CATEGORIES_SOURCE_PATH) as file:
        categories = json.load(file)
    return categories


def retrieve_products():
    """
        [{
        "id": "000f20cf84074a6ab9d8f509ac398061",
        "name": "Mũ Bảo Hiểm Xe Máy 3/4 Royce Xh01 Có 2 Kính Nhiều Size Dành Cho Nam Nữ Chính Hãng",
        "price": 600000,
        "hot_price": 420000,
        "description": "Mũ bảo hiểm xe máy 3/4 Royce XH01 có 2 kính:- Thương hiệu: Royce helmet- Do công ty TNHH SX TM Mafa VN sản xuất- Trọng lượng: 850gr- Lót: Lớp lót làm bằng vải lưới 3 lớp, tháo rời dễ dàng để vệ sinh và thay mới.- Kính: Kính che hết mặt và kéo lên kéo xuống theo nhu cầu, kính âm nhỏ bên trong màu đen giúp chống tia UV, nếu đeo kính bên trong có thể không sử dụng được kính âm của nón.- Size mũ XH01 có 3 size :+ M: 53-54cm+ L: 55-56cm+ XL:57-58cmKhách hàng có thể đo vòng đầu theo hướng dẫn bên dưới hoặc chat với shop để được hỗ trợ:Lưu ý : Về sản phẩm hãng sẽ có cải tiến về logo, khóa, pass kính ốc, quai....để hoàn hiện hơn cho sản phẩm ( quý khách vui lòng thông cảm khi nhận sản phẩm có khác xíu về phụ kiện, thông gió...do shop chưa kịp cập nhật lại hình ảnh nha )CHÍNH SÁCH BẢO HÀNH - ĐỔI TRẢ TẠI NÓN TRÙMBảo hành:-Các dòng mũ bảo hiểm được bảo hành 12 tháng theo chính sách của hãng.-Mũ được bảo hành điện tử thông qua sàn Tiki.-Khi cần bảo hành, khách hàng hãy chat trực tiếp với Nón Trùm kèm thông tin hình ảnh của mũ để shop hỗ trợ nhanh chóng.Đổi trả mới:-Nón Trùm hỗ trợ đổi mới trong vòng 7 ngày kể từ ngày nhận cho các trường hợp mũ bị lỗi sản xuất/ sai hàng/ không ưng ý hoặc không vừa size.-Điều kiện mũ đổi: nguyên mới, nguyên kiện, chưa qua sử dụng và còn đầy đủ tem nhãn mác, không trầy xước.#Nontrum #Roycehelmet",
        "category": "Mũ 3/4",
        "attributes": "Kích cỡ, Màu sắc",
        "variants": "Size M, Size XL, Size L, Sakura, Kasma, Leopard Clock, Jaume"
    },...]
    """
    with open(PRODUCTS_SOURCE_PATH) as file:
        products = json.load(file)
    return products
