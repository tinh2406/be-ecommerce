from rest_framework.routers import DefaultRouter

from .views import ChatEventsViewSet

router = DefaultRouter(trailing_slash=False)

router.register(r"events", ChatEventsViewSet, basename="events")

urlpatterns = router.urls
