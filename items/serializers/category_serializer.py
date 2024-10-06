from functools import partial

from rest_framework.serializers import ModelSerializer, CharField

from items.models import Category
from items.services import CategoryService


class CategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'deleted_at')

    parent_id = CharField(max_length=255, required=False, allow_null=True)

    def validate(self, attrs):
        if 'parent_id' in attrs:
            parent_id = attrs.get('parent_id')
            if parent_id:
                parent = CategoryService.get(parent_id)
                attrs['parent'] = parent
        return attrs

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.parent_id:
            parent = CategoryService.get(instance.parent_id)
            data['parent'] = parent.name
        return data

    def create(self, validated_data):
        category = CategoryService.create(validated_data)
        return category

    def update(self, instance, validated_data):
        partial = validated_data.pop('partial', False)
        instance = CategoryService.update(instance, validated_data, partial=partial)
        return instance
