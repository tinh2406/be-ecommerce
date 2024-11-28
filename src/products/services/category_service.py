from core.services import BaseDeleteService, BaseRetrieveService
from products.domains import CategoryDomain, ESCategoryDomain
from products.serializers import CategorySerializer


class CategoryService(BaseDeleteService, BaseRetrieveService):

    main_domain = CategoryDomain

    @classmethod
    def create(cls, validated_category):
        category = CategoryDomain.create(validated_category)

        ESCategoryDomain.index.delay(CategorySerializer(category).data)
        return category

    @classmethod
    def update(cls, instance, validated_category):
        category = CategoryDomain.update(instance, validated_category)

        ESCategoryDomain.index.delay(CategorySerializer(category).data)
        return category

    @classmethod
    def on_delete_success(cls, pk):
        ESCategoryDomain.soft_delete.delay(pk)

    @classmethod
    def on_restore_success(cls, pk):
        ESCategoryDomain.restore.delay(pk)

    @classmethod
    def search_categories(cls, query):
        categories = ESCategoryDomain.search(query)
        return categories
