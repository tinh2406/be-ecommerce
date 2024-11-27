from rest_framework import routers

from .views import ConversationViewSet, MessageViewSet

router = routers.DefaultRouter(trailing_slash=False)
router.register(
    r"conversations/messages", MessageViewSet, basename="conversations/messages"
)
router.register(r"conversations", ConversationViewSet, basename="conversations")

urlpatterns = router.urls
