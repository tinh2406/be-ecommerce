from statistics.serializers import QueryStatisticsSerializer
from statistics.services import UserStatisticsService

from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from core.permissions import IsAdminPermission


class UserStatisticsView(ViewSet):

    permission_classes = [IsAdminPermission]

    def list(self, request):
        query = request.query_params
        query_serializer = QueryStatisticsSerializer(data=query)
        query_serializer.is_valid(raise_exception=True)
        data = UserStatisticsService.get_user_statistics(
            query_serializer.validated_data
        )
        return Response(data)
