from rest_framework.serializers import CharField, ListField, Serializer


class AttributeSerializer(Serializer):

    name = CharField(max_length=255)
    values = ListField(child=CharField(max_length=255))
