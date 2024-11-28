from celery import shared_task

from products.domains import CategoryService, ProductService
from products.models import Category, Product


@shared_task
def create_product_task(validated: dict, **kwargs) -> bool:
    if validated.get("product_id"):
        instance = Product.objects.filter(source_id=validated.get("product_id")).first()
        if instance:
            return False

    try:
        category = Category.objects.filter(
            source_id=validated.get("category_id")
        ).first()
    except Category.DoesNotExist:
        category = None
    if not category:
        category = CategoryService.create(
            {
                "name": validated.get("category_name"),
                "source_id": validated.get("category_id"),
            }
        )

    validated["category_id"] = category.id
    ProductService.create_product(validated)
    return True
