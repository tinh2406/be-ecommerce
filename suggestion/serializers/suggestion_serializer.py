from rest_framework.serializers import CharField, ListField, Serializer


class GuestSuggestionSerializer(Serializer):
    latest_ratings = ListField(child=ListField(child=CharField()))

    def validate(self, attrs):

        latest_ratings = attrs.get("latest_ratings")

        attrs["latest_ratings"] = [
            [rating.replace("-", "") for rating in ratings]
            for ratings in latest_ratings
        ]
        return attrs
