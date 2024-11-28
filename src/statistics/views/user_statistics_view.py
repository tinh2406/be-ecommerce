from statistics.domains import UserStatisticDomain
from statistics.serializers import QueryStatisticsSerializer

from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from core.permissions import IsAdminPermission


class UserStatisticsView(ViewSet):

    permission_classes = [IsAdminPermission]

    def list(self, request):
        query = request.query_params
        query_serializer = QueryStatisticsSerializer(data=query)
        query_serializer.is_valid(raise_exception=True)
        data = UserStatisticDomain.get_user_statistics(query_serializer.validated_data)
        return Response(data)
