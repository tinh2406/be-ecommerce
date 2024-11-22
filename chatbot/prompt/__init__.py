from chatbot.constants import NavigateCommand

GET_SEARCH_PRODUCT_PARAMS_PROMPT = """Bạn đang cần hiểu xem câu hỏi của người dùng, dưới đây là các tham số truy vấn từ
        một câu hỏi của người dùng. Đối với từng tham số, hãy liệt kê các giá trị có thể xác định từ câu hỏi
        của người dùng. Các tham số cần xác định:
        keyword – Từ khóa mà người dùng muốn tìm kiếm sản phẩm.
        category – Danh mục sản phẩm mà người dùng muốn tìm kiếm.
        price_from – Giá tối thiểu mà người dùng muốn tìm kiếm. Hãy convert thành giá trị số.
        price_to – Giá tối đa mà người dùng muốn tìm kiếm. Hãy convert thành giá trị số.
        order_by – Tiêu chí sắp xếp theo yêu cầu của người dùng có thể có (chỉ có thể là: "name", "price").
        order_type – Kiểu sắp xếp, có thể có, chỉ có thể là asc (tăng dần) hoặc desc (giảm dần).
        Ví dụ: Câu hỏi: "Tìm các sản phẩm điện thoại từ 10 triệu đến 20 triệu, sắp xếp theo giá tăng dần."
        {
        "keyword": "điện thoại",
        "price_from": "10000000",
        "price_to": "20000000",
        "order_by": "price",
        "order_type": "asc"
        }""".replace(
    "  ", ""
).replace(
    "\n", ""
)

GET_COMPARE_PRODUCT_PARAMS_PROMPT = """Bạn đang cần hiểu xem câu hỏi của người dùng, bạn hãy xác định
        và trích xuất thông tin từ câu hỏi của người dùng để tìm sản phẩm cần so sánh, bao gồm các trường sau:
        {
        urls: Đường dẫn trang chi tiết của các sản phẩm, nếu có.
        product_ids: ID của các sản phẩm cần so sánh, nếu có.
        product_names: Tên của các sản phẩm, nếu có.
        }
        Quy trình:
        1.	Nếu câu hỏi của người dùng chứa ít nhất 2 thông tin về sản phẩm (tên, ID, hoặc URL),
        hãy điền các thông tin tương ứng cho từng trường.
        2.	Trả về kết quả trong định dạng JSON, với các trường chỉ xuất hiện nếu có dữ liệu.
        Ví dụ:
        Câu hỏi: “So sánh iPhone 14 và Samsung Galaxy S23 về giá và đánh giá của người dùng.”
        {
        "product_names": ["iPhone 14", "Samsung Galaxy S23"]
        }
        Ví dụ:
        Câu hỏi: “Tôi muốn so sánh các sản phẩm có ID là 123 và iPhone 14 về tính năng.”
        {
        "product_ids": ["123"],
        "product_names": ["iPhone 14"]
        }
        Ví dụ:
        Câu hỏi: "Tôi muốn so sánh sản phẩm có url là https://localhost:3000/product/123 và Iphone 14"
        Kết quả:
        {
        "product_names": ["Iphone 13", "Iphone 14"]
        }""".replace(
    "  ", ""
).replace(
    "\n", ""
)


GET_DETAIL_PRODUCT_PARAMS_PROMPT = """Bạn đang cần hiểu xem câu hỏi của người dùng,
        hãy giúp tôi lấy các thông tin cần thiết từ câu hỏi của người dùng khi họ muốn
        truy vấn thông tin chi tiết của một sản phẩm. Các thông tin có thể gồm:
        url – Đường dẫn trang chi tiết của sản phẩm (nếu người dùng cung cấp).
        product_id – ID của sản phẩm (nếu người dùng cung cấp hoặc ngụ ý đến sản phẩm cụ thể).
        name – Tên của sản phẩm mà người dùng muốn truy cập.

        Dựa trên câu hỏi của người dùng, xác định và trích xuất các giá trị có thể có cho mỗi thông tin.
        Ví dụ:
        Câu hỏi: "Tôi muốn xem trang chi tiết của sản phẩm ID 12345."
        Trả lời:
        {"product_id": "12345"}
        Câu hỏi: "Tôi cần chi tiết cho sản phẩm có url là https://localhost:3000/product/123."
        Trả lời:
        {"url": "https://localhost:3000/product/123"}""".replace(
    "  ", ""
).replace(
    "\n", ""
)

GET_NAVIGATION_TYPE_PROMPT = f"""Hãy phân loại câu hỏi dưới đây của khách hàng vào một trong các loại điều hướng sau:
        {NavigateCommand.GO_TO_HOME} – Điều hướng đến trang chủ.
        {NavigateCommand.GO_TO_PROFILE} – Điều hướng đến trang hồ sơ cá nhân.
        {NavigateCommand.GO_TO_SETTINGS} – Điều hướng đến trang cài đặt.
        {NavigateCommand.GO_TO_LOGOUT} – Điều hướng đến thao tác đăng xuất.
        {NavigateCommand.GO_TO_NOTIFICATION_SETTINGS} – Điều hướng đến cài đặt thông báo.
        {NavigateCommand.GO_TO_PASSWORD_SETTINGS} – Điều hướng đến cài đặt mật khẩu.
        {NavigateCommand.GO_TO_PRIVACY_SETTINGS} – Điều hướng đến cài đặt quyền riêng tư.
        {NavigateCommand.GO_TO_LANGUAGE_SETTINGS} – Điều hướng đến cài đặt ngôn ngữ.
        {NavigateCommand.GO_TO_CART} – Điều hướng đến trang giỏ hàng.
        {NavigateCommand.GO_TO_WISHLIST} – Điều hướng đến danh sách yêu thích.
        {NavigateCommand.GO_TO_ORDER_HISTORY} – Điều hướng đến lịch sử đơn hàng.
        {NavigateCommand.GO_TO_TRACK_ORDER} – Điều hướng đến trang theo dõi đơn hàng.
        "error" – Nếu không thể xác định lệnh điều hướng từ câu hỏi của khách hàng.
        Ví dụ:
        Câu hỏi: “Đi tới giỏ hàng của tôi.”
        {{“type”: {NavigateCommand.GO_TO_CART}}}
        Câu hỏi: “Tôi muốn xem cài đặt quyền riêng tư.”
        {{“type”: {NavigateCommand.GO_TO_PRIVACY_SETTINGS}}}""".replace(
    "  ", ""
).replace(
    "\n", ""
)


GET_TYPE_ACTION_PROMPT = """Bạn đang cần hiểu xem câu hỏi của người dùng,
        hãy lấy các thông tin cần thiết từ câu hỏi của người dùng khi họ muốn
        thực hiện 1 hành động đối với 1 sản phẩm. Các thông tin có thể gồm:
        url – Đường dẫn trang chi tiết của sản phẩm (nếu người dùng cung cấp).
        product_id – ID của sản phẩm (nếu người dùng cung cấp hoặc ngụ ý đến sản phẩm cụ thể).
        product_name – Tên của sản phẩm mà người dùng muốn truy cập.
        action - Hành động mà người dùng muốn thực hiện ("add_to_cart", "add_to_wishlist").
        Ví dụ:
        Câu hỏi: "Thêm giúp tôi sản phẩm có ID 12345 vào giỏ hàng."
        Trả lời:
        {"product_id": "12345", "action": "add_to_cart"}
        Ví dụ:
        Câu hỏi: "Thêm giúp tôi iphone14 vào danh sách yêu thích."
        Trả lời:
        {"product_name": "iPhone 14", "action": "add_to_wishlist"}""".replace(
    "  ", ""
).replace(
    "\n", ""
)
