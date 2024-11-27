from rest_framework.serializers import ChoiceField, Serializer


class RatingSerializer(Serializer):

    rating = ChoiceField(choices=[(0, "0"), (1, "1"), (2, "2")])
