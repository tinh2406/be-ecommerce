from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from suggestion.serializers import GuestSuggestionSerializer
from suggestion.services import SuggestionsService


class SuggestionViewSet(ModelViewSet):

    permission_classes: list[object] = []

    def create(self, request, *args, **kwargs):
        if request.user.id:
            products = SuggestionsService.get_suggestion(request.user.id)
        else:
            serializer = GuestSuggestionSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            products = SuggestionsService.get_suggestion(
                latest_ratings=serializer.data["latest_ratings"]
            )
        return Response(products)

    @action(detail=True, methods=["post"])
    def nearest(self, request, *args, **kwargs):
        product_id = kwargs.get("pk")

        if request.user.id:
            products = SuggestionsService.get_suggestion(
                request.user.id, product_id=product_id
            )
        else:
            serializer = GuestSuggestionSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors)

            products = SuggestionsService.get_suggestion(
                latest_ratings=serializer.data["latest_ratings"], product_id=product_id
            )
        return Response(products)
