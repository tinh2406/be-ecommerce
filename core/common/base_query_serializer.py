from rest_framework.serializers import Serializer, CharField, IntegerField, ChoiceField


class BaseQuerySerializer(Serializer):
    text = CharField(allow_blank=True, allow_null=True, required=False)

    page_size = IntegerField(allow_null=True, required=False)
    page = IntegerField(allow_null=True, required=False)
    skip = IntegerField(allow_null=True, required=False)
    order_by = ChoiceField(allow_null=True, required=False, choices=['name', 'id'])
    order_type = ChoiceField(allow_null=True, required=False, choices=['asc', 'desc'])

    def to_representation(self, instance):
        if instance.get('text') == '':
            instance.pop('text')

        if instance.get('page_size') is None or instance.get('page_size') < 1 or instance.get('page_size') > 100:
            instance['page_size'] = 10
        if instance.get('page') is None or instance.get('page') < 1:
            instance['page'] = 1
        instance['skip'] = (instance['page'] - 1) * instance['page_size']

        return instance

