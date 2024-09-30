from rest_framework import routers
from .views import AuthViewSet, UserViewSet

router = routers.DefaultRouter(trailing_slash=False)
router.register(r'', AuthViewSet, basename="auth")
router.register(r'users', UserViewSet, basename="user")

urlpatterns = router.urls
