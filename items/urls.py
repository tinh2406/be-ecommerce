from rest_framework import routers

from items.views import CategoryViewSet

router = routers.DefaultRouter(trailing_slash=False)
router.register(r"categories", CategoryViewSet, basename="categories")

urlpatterns = router.urls
