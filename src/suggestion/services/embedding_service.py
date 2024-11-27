# Load model directly
import torch
from transformers import AutoModel, AutoTokenizer

from core.settings import BASE_DIR


def load_stopwords(file_path: str) -> set:
    with open(file_path) as f:
        vietnamese = f.read().splitlines()
        stopwords = set(vietnamese)

    return stopwords


def embedding_products(
    products: list[dict],
    tokenizer: AutoTokenizer,
    model: AutoModel,
    device: str,
    stopwords: set,
) -> tuple[list[int], list[torch.Tensor]]:
    ids = [item["id"] for item in products]
    names = [item["name"] for item in products]
    categories = [item["category"] for item in products]
    descriptions = [
        (
            " ".join(
                [word for word in item["description"].split() if word not in stopwords]
            )
            if item["description"]
            else ""
        )
        for item in products
    ]

    encode_names = tokenizer(
        names, return_tensors="pt", padding=True, truncation=True, max_length=128
    ).to(device)
    inputs_name = encode_names["input_ids"]
    name_attention_mask = encode_names["attention_mask"]

    encode_descriptions = tokenizer(
        descriptions, return_tensors="pt", padding=True, truncation=True, max_length=128
    ).to(device)
    inputs_description = encode_descriptions["input_ids"]
    description_attention_mask = encode_descriptions["attention_mask"]

    encode_categories = tokenizer(
        categories, return_tensors="pt", padding=True, truncation=True, max_length=128
    ).to(device)
    inputs_category = encode_categories["input_ids"]
    category_attention_mask = encode_categories["attention_mask"]

    with torch.no_grad():
        outputs_name = model(inputs_name, attention_mask=name_attention_mask)
        embeddings_name = outputs_name.last_hidden_state

        outputs_description = model(
            inputs_description, attention_mask=description_attention_mask
        )
        embeddings_description = outputs_description.last_hidden_state

        outputs_category = model(
            inputs_category, attention_mask=category_attention_mask
        )
        embeddings_category = outputs_category.last_hidden_state

    embeddings = []
    for i in range(len(ids)):
        common_embedding = (
            3 * embeddings_name[i][0]
            + 2 * embeddings_description[i][0]
            + embeddings_category[i][0]
        )
        embeddings.append(common_embedding.cpu().numpy())

    return ids, embeddings


path = f"{BASE_DIR}/suggestion/data"


class EmbeddingService:
    batch_size = 16
    model_name = "vinai/phobert-base-v2"

    stopwords = load_stopwords(f"{path}/vietnamese.txt")
    device: str = torch.device("mps" if torch.mps.is_available() else "cpu")

    # TODO uncomment this code
    tokenizer = AutoTokenizer.from_pretrained(model_name, output_hidden_states=True)
    model_embedding = AutoModel.from_pretrained(model_name)
    model_embedding.to(device)

    @classmethod
    def embedding(
        cls, products: list[dict] | dict
    ) -> tuple[list[int], list[torch.Tensor]] | tuple[int, torch.Tensor]:
        if type(products) is list:
            ids, embeddings = [], []
            for i in range(0, len(products), cls.batch_size):
                batch = products[i : i + cls.batch_size]
                _ids, _embeddings = embedding_products(
                    batch, cls.tokenizer, cls.model_embedding, cls.device, cls.stopwords
                )
                ids.extend(_ids)
                embeddings.extend(_embeddings)

            return ids, embeddings
        elif type(products) is dict:
            products = [products]
            ids, embeddings = embedding_products(
                products, cls.tokenizer, cls.model_embedding, cls.device, cls.stopwords
            )
            return ids[0], embeddings[0]

        raise ValueError("Invalid input")
