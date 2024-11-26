from statistics.constants import CycleConstant

from rest_framework.serializers import ChoiceField, DateField, IntegerField, Serializer


class QueryStatisticsSerializer(Serializer):

    num_cycle = IntegerField(required=False)
    cycle = ChoiceField(choices=CycleConstant.CycleChoice)
    start_date = DateField(required=False)
    end_date = DateField(required=False)
