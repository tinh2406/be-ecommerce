import json
import time

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

from core.settings import BASE_DIR

model_name = "dangvantuan/vietnamese-embedding"

CHUNK_SIZE = 650
CHUNK_OVERLAP = 250
BATCH_SIZE = 200


embedding_function = HuggingFaceEmbeddings(model_name=model_name)

CATEGORY_SOURCE_PATH = f"{BASE_DIR}/suggestion/data/categories.json"
PRODUCT_SOURCE_PATH = f"{BASE_DIR}/suggestion/data/products.json"
CATEGORY_STORE = f"{BASE_DIR}/chatbot/data/categories_store"
PRODUCT_STORE = f"{BASE_DIR}/chatbot/data/products_store"
OTHER_DATA_STORE = f"{BASE_DIR}/chatbot/data/other_store"


def load_categories_data():
    with open(CATEGORY_SOURCE_PATH, "rb") as f:
        categories = json.load(f)

    data, metadata_list = [], []
    for item in categories:
        data.append(f"danh mục {item['name']}")
        data.append(f"thể loại {item['name']}")
        metadata_list.append({"danh mục": json.dumps(item, ensure_ascii=False)})
        metadata_list.append({"thể loại": json.dumps(item, ensure_ascii=False)})

    data.append("các loại sản phẩm")
    metadata_list.append(
        {
            "các loại sản phẩm": "sách, truyện, đồ dùng gia đình, xe máy, xe đạp, dụng cụ xe máy, trang phục, ..."
        }
    )

    data.append("bao nhiêu loại sản phẩm")
    metadata_list.append(
        {
            "các loại sản phẩm": "sách, truyện, đồ dùng gia đình, xe máy, xe đạp, dụng cụ xe máy, trang phục, ..."
        }
    )

    return data, metadata_list


def load_products_data():
    with open(PRODUCT_SOURCE_PATH, "rb") as f:
        products = json.load(f)

    data, metadata_list = [], []
    for item in products:
        data.append(f"sản phẩm id {item['id']}")
        data.append(f"sản phẩm {item['name']}")
        data.append(f"mặt hàng {item['name']}")
        data.append(f"thuộc danh mục {item['category']}")
        data.append(f"thuộc thể loại {item['category']}")

        item.pop("description", None)

        metadata_list.append({"sản phẩm": json.dumps(item, ensure_ascii=False)})
        metadata_list.append({"sản phẩm": json.dumps(item, ensure_ascii=False)})
        metadata_list.append({"sản phẩm": json.dumps(item, ensure_ascii=False)})
        metadata_list.append({"sản phẩm": json.dumps(item, ensure_ascii=False)})
        metadata_list.append({"sản phẩm": json.dumps(item, ensure_ascii=False)})

    data.append("các sản phẩm")
    metadata_list.append(
        {
            "sản phẩm": "sách, truyện, đồ dùng gia đình, xe máy, xe đạp, dụng cụ xe máy, trang phục, ..."
        }
    )

    data.append("bao nhiêu sản phẩm")
    metadata_list.append(
        {
            "sản phẩm": "sách, truyện, đồ dùng gia đình, xe máy, xe đạp, dụng cụ xe máy, trang phục, ..."
        }
    )

    return data, metadata_list


def load_other_data():
    data = [
        "xem trang cá nhân",
        "xem thông tin cá nhân",
        "xem thông tin tài khoản",
        "xem thông tin người dùng",
        "cập nhật thông tin cá nhân",
        "cập nhật thông tin tài khoản",
        "cập nhật thông tin người dùng",
        "đổi mật khẩu",
        "cập nhật mật khẩu",
        "đổi mật khẩu tài khoản",
        "cập nhật mật khẩu tài khoản",
        "đổi mật khẩu người dùng",
        "cập nhật mật khẩu người dùng",
        "cập nhật thông tin bảo mật",
        "cập nhật email",
        "cập nhật số điện thoại",
        "cập nhật địa chỉ",
        "cài đặt ngôn ngữ",
        "cài đặt ngôn ngữ cho tài khoản",
        "xem giỏ hàng",
        "xem danh sách yêu thích",
    ]

    metadata_list = [
        "GO_TO_PROFILE",
        "GO_TO_PROFILE",
        "GO_TO_PRIVACY_SETTINGS",
        "GO_TO_PROFILE",
        "GO_TO_PROFILE",
        "GO_TO_PRIVACY_SETTINGS",
        "GO_TO_PROFILE",
        "GO_TO_PASSWORD_SETTINGS",
        "GO_TO_PASSWORD_SETTINGS",
        "GO_TO_PASSWORD_SETTINGS",
        "GO_TO_PASSWORD_SETTINGS",
        "GO_TO_PASSWORD_SETTINGS",
        "GO_TO_PASSWORD_SETTINGS",
        "GO_TO_PRIVACY_SETTINGS",
        "GO_TO_PRIVACY_SETTINGS",
        "GO_TO_PROFILE",
        "GO_TO_PROFILE",
        "GO_TO_LANGUAGE_SETTINGS",
        "GO_TO_WISHLIST",
        "GO_TO_CART",
        "GO_TO_ORDER_HISTORY",
    ]
    return data, [{"url": metadata} for metadata in metadata_list]


def create_vectordb():
    start_time = time.time()
    data_categories, metadata_list_categories = load_categories_data()
    data_products, metadata_list_products = load_products_data()
    data_other, metadata_list_other = load_other_data()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP
    )
    categories_docs = text_splitter.create_documents(
        data_categories, metadatas=metadata_list_categories
    )
    products_docs = text_splitter.create_documents(
        data_products, metadatas=metadata_list_products
    )
    other_docs = text_splitter.create_documents(
        data_categories + data_products + data_other,
        metadatas=metadata_list_categories
        + metadata_list_products
        + metadata_list_other,
    )

    categories_store = Chroma(
        embedding_function=embedding_function,
        persist_directory=CATEGORY_STORE,
    )
    products_store = Chroma(
        embedding_function=embedding_function,
        persist_directory=PRODUCT_STORE,
    )
    other_store = Chroma(
        embedding_function=embedding_function,
        persist_directory=OTHER_DATA_STORE,
    )

    for store, docs in zip(
        [categories_store, products_store, other_store],
        [categories_docs, products_docs, other_docs],
    ):
        batches = [docs[i : i + BATCH_SIZE] for i in range(0, len(docs), BATCH_SIZE)]
        for batch in batches:
            store.add_documents(documents=batch)

    end_time = round((time.time() - start_time) / (60), 2)
    print(f"VectorDB is created in {end_time} mins")


def search_categories(query):
    vectorstore = Chroma(
        embedding_function=embedding_function,
        persist_directory=CATEGORY_STORE,
    )
    results = vectorstore.similarity_search_with_score(query, k=3)
    return [
        {"data": result[0].page_content, "metadata": result[0].metadata}
        for result in results
    ]


def search_products(query):
    vectorstore = Chroma(
        embedding_function=embedding_function,
        persist_directory=PRODUCT_STORE,
    )
    results = vectorstore.similarity_search_with_score(query, k=3)
    return [
        {"data": result[0].page_content, "metadata": result[0].metadata}
        for result in results
    ]


def search_other(query):
    vectorstore = Chroma(
        embedding_function=embedding_function,
        persist_directory=OTHER_DATA_STORE,
    )
    results = vectorstore.similarity_search_with_score(query, k=3)
    return [
        {"data": result[0].page_content, "metadata": result[0].metadata}
        for result in results
    ]
