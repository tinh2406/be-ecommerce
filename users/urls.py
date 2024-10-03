from rest_framework import routers
from .views import AuthViewSet, UserViewSet, AddressViewSet

router = routers.DefaultRouter(trailing_slash=False)
router.register(r'', AuthViewSet, basename="auth")
router.register(r'users', UserViewSet, basename="user")
router.register(r'addresses', AddressViewSet, basename="address")

urlpatterns = router.urls
