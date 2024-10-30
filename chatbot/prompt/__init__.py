CLASSIFIER_QUESTION_PROMPT = """
Hãy phân loại câu hỏi dưới đây của khách hàng vào một trong các loại lệnh sau:

list_products – Liệt kê sản phẩm theo mô tả và sắp xếp theo yêu cầu.
get_product_details – Giới thiệu chi tiết một sản phẩm.
compare_products – So sánh các sản phẩm theo các tiêu chí nhất định.
get_purchase_history – Liệt kê lịch sử mua hàng.
get_order_status – Kiểm tra tình trạng hiện tại của các đơn hàng.
add_to_cart – Thêm sản phẩm vào giỏ hàng.
navigate_to_page – Điều hướng đến trang chính.
contact_support – Hỗ trợ liên hệ chăm sóc khách hàng.
gossip - Nói chuyện phiếm
Trả về kết quả sau khi phân loại.

Ví dụ:

Câu hỏi: "Liệt kê các sản phẩm laptop có giá từ 15 triệu đến 20 triệu và sắp xếp theo đánh giá tốt nhất."
{
"type": "list_products"
}

Dưới đây là câu hỏi cần phân loại:

"""


GET_PRODUCT_LIST_PROMPT = """
Dưới đây là các tham số truy vấn từ một câu hỏi của người dùng. Đối với từng tham số, hãy liệt kê các giá trị có thể có hoặc cách thức để xác định giá trị từ nội dung của câu hỏi. Giải thích ngắn gọn cách xác định các giá trị này khi có thể.

Các tham số cần xác định:

keyword – Từ khóa mà người dùng muốn tìm kiếm sản phẩm.
category_name – Từ khóa của tên của danh mục sản phẩm mà người dùng đang quan tâm.
price_from – Giá tối thiểu mà người dùng muốn tìm kiếm.
price_to – Giá tối đa mà người dùng muốn tìm kiếm.
order_by – Tiêu chí sắp xếp theo yêu cầu của người dùng (ví dụ: giá, ngày tạo, hoặc thứ hạng).
order_type – Kiểu sắp xếp, có thể là asc (tăng dần) hoặc desc (giảm dần).
Ví dụ:

Câu hỏi: "Tìm các sản phẩm điện thoại từ 10 triệu đến 20 triệu, sắp xếp theo giá tăng dần."
keyword: "điện thoại"
price_from: "10 triệu"
price_to: "20 triệu"
order_by: "giá"
order_type: "asc"
Câu hỏi của người dùng: """

GET_PRODUCT_DETAILS_PROMPT = """
Hãy giúp tôi lấy các thông tin cần thiết từ câu hỏi của người dùng khi họ muốn truy cập trang chi tiết của một sản phẩm. Các thông tin có thể gồm:

url – Đường dẫn trang chi tiết của sản phẩm (nếu người dùng cung cấp).
product_id – ID của sản phẩm (nếu người dùng cung cấp hoặc ngụ ý đến sản phẩm cụ thể).
product_name – Tên của sản phẩm mà người dùng muốn truy cập.
Dựa trên câu hỏi của người dùng, xác định và trích xuất các giá trị có thể có cho mỗi thông tin. Nếu có từ khóa nào trong câu hỏi cho thấy ý định muốn xem chi tiết sản phẩm, hãy chỉ rõ.

Ví dụ:

Câu hỏi: "Tôi muốn xem trang chi tiết của sản phẩm ID 12345"

product_id: "12345"
Câu hỏi: "Tôi cần chi tiết cho sản phẩm iPhone 14"

product_name: "iPhone 14"
Câu hỏi của người dùng: """


COMPARE_PRODUCT_PROMPT = """
Dưới đây là một câu hỏi của người dùng muốn so sánh ít nhất hai sản phẩm. Hãy giúp tôi xác định các thông tin và giá trị cần thiết cho yêu cầu so sánh này, bao gồm:

urls – Đường dẫn trang chi tiết của các sản phẩm (nếu người dùng cung cấp).
product_ids – ID của các sản phẩm cần so sánh (nếu người dùng cung cấp).
product_names – Tên của các sản phẩm nếu ID không có sẵn (hoặc khi người dùng đề cập tên trực tiếp).

Dựa trên câu hỏi của người dùng, hãy trích xuất các giá trị tương ứng cho từng thông tin. Nếu có bất kỳ từ khóa nào trong câu hỏi ngụ ý tiêu chí so sánh, hãy chỉ rõ tiêu chí đó.

Ví dụ:

Câu hỏi: "So sánh iPhone 14 và Samsung Galaxy S23 về giá và đánh giá của người dùng."
product_names: ["iPhone 14", "Samsung Galaxy S23"]
Câu hỏi: "Tôi muốn so sánh các sản phẩm có ID là 123 và 456 về tính năng."
product_ids: ["123", "456"]

Câu hỏi của người dùng: """


GET_ORDERS_STATUS_PROMPT = """
Dưới đây là câu hỏi của người dùng về trạng thái đơn đặt hàng. Hãy xác định và trích xuất các thông tin cần thiết để xử lý yêu cầu này, bao gồm:

order_status – Trạng thái đơn hàng mà người dùng quan tâm (ví dụ: PENDING, ACCEPTED, DELIVERED, CANCELED).
total_order_flag – Đánh dấu có nếu người dùng muốn tính tổng số đơn hàng.
total_item_flag – Đánh dấu có nếu người dùng muốn tính tổng sản phẩm.
list_flag – Đánh dấu người dùng có muốn liệt kê các order theo yêu cầu không.
date_from – Khoảng thời gian mà người dùng muốn truy vấn đơn hàng (nếu có).
date_to - Khoảng thời gian mà người dùng muốn truy vấn đơn hàng (nếu có).
Dựa trên câu hỏi của người dùng, hãy xác định và trích xuất các giá trị phù hợp cho từng thông tin trên, bao gồm việc xác định nếu người dùng muốn tính tổng hay liệt kê chi tiết.

Ví dụ:

Câu hỏi: "Tôi còn bao nhiêu đơn hàng chưa nhận?"
order_status: ["PENDING", "ACCEPTED"]
total_order_flag: "true"
list_flag: "false"
total_item_flag: "false"

Câu hỏi: "Liệt kê cho tôi các đơn hàng đã giao từ đầu năm nay."
order_status: "DELIVERED"
total_flag: "false"
date_range: "1/1/2024"
Câu hỏi của người dùng: """