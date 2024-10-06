from items.views import CategoryViewSet
from rest_framework import routers

router = routers.DefaultRouter(trailing_slash=False)
router.register(r'categories', CategoryViewSet, basename="categories")

urlpatterns = router.urls
