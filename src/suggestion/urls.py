from rest_framework import routers

from src.suggestion.views import RatingViewSet, SuggestionViewSet

router = routers.DefaultRouter(trailing_slash=False)
router.register(r"ratings", RatingViewSet, basename="ratings")
router.register(r"suggestions", SuggestionViewSet, basename="suggestions")

urlpatterns = router.urls
