from rest_framework import routers

from items.views import CategoryViewSet, ItemViewSet

router = routers.DefaultRouter(trailing_slash=False)
router.register(r"categories", CategoryViewSet, basename="categories")
router.register(r"items", ItemViewSet, basename="items")

urlpatterns = router.urls
