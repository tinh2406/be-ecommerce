from rest_framework.serializers import Serializer, CharField, IntegerField, ChoiceField


class BaseQuerySerializer(Serializer):
    text = CharField(allow_blank=True, allow_null=True, required=False)

    page_size = IntegerField(allow_null=True, required=False)
    page = IntegerField(allow_null=True, required=False)
    skip = IntegerField(allow_null=True, required=False)
    order_by = ChoiceField(allow_null=True, required=False, choices=['name', 'id'])
    order_type = ChoiceField(allow_null=True, required=False, choices=['asc', 'desc'])

    def validate(self, attrs):
        if attrs.get('text') == '':
            attrs.pop('text')

        if attrs.get('page_size') is None or attrs.get('page_size') < 1 or attrs.get('page_size') > 100:
            attrs['page_size'] = 10
        if attrs.get('page') is None or attrs.get('page') < 1:
            attrs['page'] = 1
        attrs['skip'] = (attrs['page'] - 1) * attrs['page_size']

        return attrs
