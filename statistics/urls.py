from rest_framework import routers

from .views import ProductStatisticsView, UserStatisticsView

router = routers.DefaultRouter(trailing_slash=False)
router.register(r"users", UserStatisticsView, basename="users")
router.register(r"products", ProductStatisticsView, basename="products")

urlpatterns = router.urls
