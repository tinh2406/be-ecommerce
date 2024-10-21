from rest_framework import routers

from .views import ProductMapperViewSet, ProductsMapperViewSet

router = routers.DefaultRouter(trailing_slash=False)
router.register(r"product-mappers", ProductMapperViewSet, basename="product-mappers")
router.register(r"products-mappers", ProductsMapperViewSet, basename="products-mappers")

urlpatterns = router.urls
