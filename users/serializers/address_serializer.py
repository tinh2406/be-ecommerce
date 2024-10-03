from rest_framework.serializers import ModelSerializer

from users.constants import Cities, Wards, Districts
from users.models import Address


class AddressSerializer(ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'
        read_only_fields = ('user',)

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['city_detail'] = Cities.DICT.get(instance.city)
        ret['district_detail'] = Districts(instance.city).DICT.get(instance.district)
        ret['ward_detail'] = Wards(instance.ward).DICT.get(instance.ward)
        ret['detail'] = instance.detail
        return ret

    def validate(self, attrs):
        city = attrs.get('city')
        district = attrs.get('district')
        ward = attrs.get('ward')
        if city and city not in Cities.DICT:
            raise ValueError('City is invalid')
        if district and district not in Districts(city).DICT:
            raise ValueError('District is invalid')
        if ward and ward not in Wards(district).DICT:
            raise ValueError('Ward is invalid')
        return attrs

