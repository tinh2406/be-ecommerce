import threading

import torch
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from suggestion.serializers.rating_serializer import RatingSerializer
from suggestion.services import ProductSimilarityService, UserRatingService


class RatingViewSet(ModelViewSet):

    @action(detail=True, methods=["POST"])
    def real_rating(self, request, pk=None):

        serializer = RatingSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        user_id = str(user.id).replace("-", "")
        product_id = str(pk).replace("-", "")

        idx_user = UserRatingService.user_ids.index(user_id)
        idx_product = ProductSimilarityService.ids.index(product_id)
        idx_product = torch.where(
            ProductSimilarityService.sorted_products == idx_product
        )[0].item()

        if serializer.data["rating"] == 0:
            thread = threading.Thread(
                target=UserRatingService.remove_real_user_rating,
                args=(idx_user, idx_product),
            )
            thread.start()

        else:
            thread = threading.Thread(
                target=UserRatingService.add_real_user_rating,
                args=(idx_user, idx_product, serializer.data["rating"]),
            )
            thread.start()

        return Response(status=status.HTTP_200_OK)

    @action(detail=True, methods=["POST"])
    def hidden_rating(self, request, pk=None):
        serializer = RatingSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        user_id = str(user.id).replace("-", "")
        product_id = str(pk).replace("-", "")

        idx_user = UserRatingService.user_ids.index(user_id)
        idx_product = ProductSimilarityService.ids.index(product_id)
        idx_product = torch.where(
            ProductSimilarityService.sorted_products == idx_product
        )[0].item()

        thread = threading.Thread(
            target=UserRatingService.add_hidden_user_rating,
            args=(idx_user, idx_product, serializer.data["rating"]),
        )
        thread.start()

        return Response(status=status.HTTP_200_OK)

    @action(detail=True, methods=["POST"])
    def disinterest_rating(self, request, pk=None):

        user = request.user
        user_id = str(user.id).replace("-", "")
        product_id = str(pk).replace("-", "")

        idx_user = UserRatingService.user_ids.index(user_id)
        idx_product = ProductSimilarityService.ids.index(product_id)
        idx_product = torch.where(
            ProductSimilarityService.sorted_products == idx_product
        )[0].item()

        thread = threading.Thread(
            target=UserRatingService.add_disinterest,
            args=(
                idx_user,
                idx_product,
            ),
        )
        thread.start()

        return Response(status=status.HTTP_200_OK)
