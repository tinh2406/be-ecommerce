from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from suggestion.domains import RatingDomain
from suggestion.serializers.rating_serializer import RatingSerializer


class RatingViewSet(ModelViewSet):

    @action(detail=True, methods=["POST"])
    def real_rating(self, request, pk=None):

        serializer = RatingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        RatingDomain.real_rating(
            request.user.id,
            pk,
            serializer.data["rating"],
        )

        return Response(status=status.HTTP_200_OK)

    @action(detail=True, methods=["POST"])
    def hidden_rating(self, request, pk=None):
        serializer = RatingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        RatingDomain.hidden_rating(
            request.user.id,
            pk,
            serializer.data["rating"],
        )

        return Response(status=status.HTTP_200_OK)

    @action(detail=True, methods=["POST"])
    def disinterest_rating(self, request, pk=None):

        RatingDomain.disinterest_rating(
            request.user.id,
            pk,
        )

        return Response(status=status.HTTP_200_OK)
