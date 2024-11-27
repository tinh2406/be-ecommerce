from rest_framework import routers

from .views import CategoryViewSet, ProductViewSet

router = routers.DefaultRouter(trailing_slash=False)
router.register(r"categories", CategoryViewSet, basename="categories")
router.register(r"products", ProductViewSet, basename="products")

urlpatterns = router.urls
