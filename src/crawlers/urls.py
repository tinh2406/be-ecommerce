from rest_framework import routers

from .views import CrawlerViewSet, ProductMapperViewSet, ProductsMapperViewSet

router = routers.DefaultRouter(trailing_slash=False)
router.register(r"product-mappers", ProductMapperViewSet, basename="product-mappers")
router.register(r"products-mappers", ProductsMapperViewSet, basename="products-mappers")
router.register(r"crawlers", CrawlerViewSet, basename="crawlers")

urlpatterns = router.urls
