from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

from core.settings import BASE_DIR

model_name = "dangvantuan/vietnamese-embedding"

CHUNK_SIZE = 650
CHUNK_OVERLAP = 250
BATCH_SIZE = 200

embedding_function = HuggingFaceEmbeddings(model_name=model_name)

CATEGORY_STORE = f"{BASE_DIR}/chatbot/data/categories_store"
PRODUCT_STORE = f"{BASE_DIR}/chatbot/data/products_store"
OTHER_DATA_STORE = f"{BASE_DIR}/chatbot/data/other_store"


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
