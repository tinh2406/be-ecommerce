from rest_framework import routers
from .views import AuthViewSet

router = routers.DefaultRouter(trailing_slash=False)
router.register(r'', AuthViewSet, basename="auth")

urlpatterns = router.urls
