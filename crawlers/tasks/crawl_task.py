import re

import requests
from celery import shared_task

from crawlers.models import ProductMapper
from crawlers.services.product_mapper_service import ProductMapperService
from crawlers.services.products_mapper_service import ProductsMapperService
from crawlers.services.request_params_service import RequestParamsService
from products.services import ProductService


class NotFoundKeyException(Exception):
    pass


def get_value_by_nested_key(data, key, is_required=False):
    value = data
    if key is None:
        if is_required:
            raise NotFoundKeyException(f"Key {key} is required")
        return None
    for k in key.split("/"):
        value = value.get(k)
        if value is None and is_required:
            raise NotFoundKeyException(f"Key {k} is not valid")
    return value


def remove_html_tags(text=None):
    if text is None:
        return None
    clean = re.compile("<.*?>")
    return re.sub(clean, "", text)


def remove_tiki_text_extension(text=None):
    if text is None:
        return None
    text = text.split("Giá sản phẩm trên Tiki đã bao gồm thuế theo luật hiện hành.")[0]
    return text


def extract_product_data(data, product_mapper: ProductMapper):
    """Extracts product data based on product mapper fields."""
    return {
        "product_id": get_value_by_nested_key(
            data, product_mapper.product_id, is_required=True
        ),
        "name": get_value_by_nested_key(
            data, product_mapper.product_name, is_required=True
        ),
        "description": remove_tiki_text_extension(
            remove_html_tags(
                get_value_by_nested_key(data, product_mapper.product_description)
            )
        ),
        "price": get_value_by_nested_key(
            data, product_mapper.product_price, is_required=True
        ),
        "hot_price": get_value_by_nested_key(data, product_mapper.product_hot_price),
        "created_at": get_value_by_nested_key(data, product_mapper.product_created_at),
        "updated_at": get_value_by_nested_key(data, product_mapper.product_updated_at),
        "deleted_at": get_value_by_nested_key(data, product_mapper.product_deleted_at),
        "thumbnail": get_value_by_nested_key(
            data, product_mapper.product_thumbnail, is_required=True
        ),
        "category_id": get_value_by_nested_key(
            data, product_mapper.product_category_id, is_required=True
        ),
        "category_name": get_value_by_nested_key(
            data, product_mapper.product_category_name, is_required=True
        ),
    }


def extract_images(data, product_mapper: ProductMapper):
    """Extracts product images based on product mapper fields."""
    images = get_value_by_nested_key(data, product_mapper.product_images)

    return [
        (
            get_value_by_nested_key(image, product_mapper.product_images_name)
            if product_mapper.product_images_name
            else image
        )
        for image in images
    ]


def extract_variants(data, product_mapper: ProductMapper, attributes):
    """Extracts product variants based on provided attributes."""

    # Mapping attribute names to their respective codes
    attribute_mapping = {
        attr[product_mapper.attribute_name]: attr[product_mapper.attribute_code]
        for attr in attributes
    }

    # Initialize variants list
    variants = []

    # Retrieve the list of variants from data
    variant_list = get_value_by_nested_key(
        data, product_mapper.variants, is_required=True
    )

    for variant in variant_list:
        # Create a dictionary for each variant with price, hot_price, and image
        product_variant = {
            "price": get_value_by_nested_key(
                variant, product_mapper.variant_price, is_required=True
            ),
            "hot_price": get_value_by_nested_key(
                variant, product_mapper.variant_hot_price
            ),
            "image": get_value_by_nested_key(
                variant, product_mapper.variant_image, is_required=True
            ),
        }

        # Add attributes to the product variant
        for attr in attributes:
            attribute_name = attr[product_mapper.attribute_name]
            product_variant[attribute_name] = get_value_by_nested_key(
                variant, attribute_mapping[attribute_name], is_required=True
            )

        # Append the complete variant to the list
        variants.append(product_variant)

    return variants


def get_one_item(url, headers, params, product_mapper_id):
    product_mapper = ProductMapperService.get(product_mapper_id)
    response = requests.get(url, headers=headers, params=params)
    data = response.json()

    product = extract_product_data(data, product_mapper)

    product["images"] = extract_images(data, product_mapper)

    attributes = get_value_by_nested_key(
        data, product_mapper.attributes, is_required=False
    )
    if attributes:
        product["attributes"] = [
            {
                "name": get_value_by_nested_key(
                    attr, product_mapper.attribute_name, is_required=True
                ),
                "values": [
                    (
                        get_value_by_nested_key(
                            value, product_mapper.attribute_value_name, is_required=True
                        )
                        if product_mapper.attribute_value_name
                        else value
                    )
                    for value in get_value_by_nested_key(
                        attr,
                        product_mapper.attribute_values,
                        is_required=True,
                    )
                ],
            }
            for attr in attributes
        ]
        product["variants"] = extract_variants(data, product_mapper, attributes)

    return product


def test_crawl_config(**kwargs):
    url = kwargs.get("url")
    headers = kwargs.get("headers") or {}
    params = kwargs.get("params") or {}

    product_mapper_id = kwargs.get("product_mapper_id")
    products_mapper_id = kwargs.get("products_mapper_id")
    products_mapper = ProductsMapperService.get(products_mapper_id)

    response = requests.get(url, headers=headers, params=params).json()

    products_response = {
        "data": get_value_by_nested_key(
            response, products_mapper.data, is_required=True
        ),
        "primary_key": get_value_by_nested_key(
            response, products_mapper.data, is_required=True
        )[0].get(products_mapper.primary_key),
        "total": get_value_by_nested_key(
            response, products_mapper.total, is_required=True
        ),
        "total_page": get_value_by_nested_key(
            response, products_mapper.total_page, is_required=True
        ),
        "take": get_value_by_nested_key(
            response, products_mapper.take, is_required=True
        ),
        "page": get_value_by_nested_key(
            response, products_mapper.page, is_required=True
        ),
    }

    get_one_item(
        f'{url}/{products_response["primary_key"]}', headers, params, product_mapper_id
    )

    return True


@shared_task(name="crawl_task")
def crawl_task(**kwargs):
    url = kwargs.get("url")
    quantity = kwargs.get("quantity")
    request_params_id = kwargs.get("request_params_id")
    request_properties = RequestParamsService.get(request_params_id)
    headers = request_properties.headers or {}
    params = request_properties.params or {}

    products_mapper_id = kwargs.get("products_mapper_id")
    products_mapper = ProductsMapperService.get(products_mapper_id)

    take_key = params.get("take_key")
    page_key = params.get("page_key")
    take = params.get(take_key)
    page = params.get(page_key)
    total_saved = params.get("total_saved", 0)

    if total_saved >= page * take:
        params[page_key] = total_saved // take + 1

    count = 0
    while count < quantity:
        response = requests.get(url, headers=headers, params=params).json()
        data_list = get_value_by_nested_key(
            response, products_mapper.data, is_required=True
        )
        if not data_list:
            break

        for item in data_list:
            if count >= quantity or total_saved >= get_value_by_nested_key(
                response, products_mapper.total, is_required=True
            ):
                break

            try:
                product_id = item.get(products_mapper.primary_key)
                product = get_one_item(
                    f"{url}/{product_id}",
                    headers,
                    params,
                    kwargs.get("product_mapper_id"),
                )
                ProductService.create_product_in_background.delay(product)
                count += 1
                total_saved += 1
            except NotFoundKeyException:
                continue
        params[page_key] += 1
        params["total_saved"] = total_saved
        RequestParamsService.update_params(request_params_id, params)

    return True
