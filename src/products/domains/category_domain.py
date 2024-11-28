from core.services import BaseDeleteDomain, BaseRetrieveDomain
from products.serializers import CategorySerializer
from products.services import CategoryService, ESCategoryService


class CategoryDomain(BaseRetrieveDomain, BaseDeleteDomain):

    @classmethod
    def create(cls, validated_category):
        category = CategoryService.create(validated_category)

        ESCategoryService.index.delay(CategorySerializer(category).data)
        return category

    @classmethod
    def update(cls, instance, validated_category):
        category = CategoryService.update(instance, validated_category)

        ESCategoryService.index.delay(CategorySerializer(category).data)
        return category

    @classmethod
    def on_delete_success(cls, pk):
        ESCategoryService.soft_delete.delay(pk)

    @classmethod
    def on_restore_success(cls, pk):
        ESCategoryService.restore.delay(pk)

    @classmethod
    def search_categories(cls, query):
        categories = ESCategoryService.search(query)
        return categories
