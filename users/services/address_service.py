from typing import Union

from django.core.cache import cache
from rest_framework.exceptions import NotFound

from users.constants import Cities, Districts, Wards
from users.models import Address


class AddressService:
    @classmethod
    def list_cities(cls, name=None, **kwargs):
        cache_key = "list_cities"
        if name:
            name = name[0].lower()
            cache_key += f"_{name}"

        cities = cache.get(cache_key)
        if cities is None:
            if name:
                cities = [
                    {"id": city[0], "name": city[1]}
                    for city in Cities.CHOICES
                    if city[1].lower().find(name) != -1
                ]
            else:
                cities = [{"id": city[0], "name": city[1]} for city in Cities.CHOICES]

        cache.set(cache_key, cities)
        return cities

    @classmethod
    def get_city(cls, city_id):
        return Cities.DICT.get(city_id)

    @classmethod
    def list_districts(cls, city_id, name=None, **kwargs):
        cache_key = f"list_districts_{city_id}"
        if name:
            name = name[0].lower()
            cache_key += f"_{name}"
        districts = cache.get(cache_key)
        if districts is None:
            if name:
                districts = [
                    {"id": district[0], "name": district[1]}
                    for district in Districts(city_id).CHOICES
                    if district[1].lower().find(name) != -1
                ]
            else:
                districts = [
                    {"id": district[0], "name": district[1]}
                    for district in Districts(city_id).CHOICES
                ]
        cache.set(cache_key, districts)
        return districts

    @classmethod
    def get_district(cls, city_id, district_id):
        return Districts(city_id).DICT.get(district_id)

    @classmethod
    def list_wards(cls, district_id, name=None, **kwargs):
        cache_key = f"list_wards_{district_id}"
        if name:
            name = name[0].lower()
            cache_key += f"_{name}"
        wards = cache.get(cache_key)
        if wards is None:
            if name:
                wards = [
                    {"id": ward[0], "name": ward[1]}
                    for ward in Wards(district_id).CHOICES
                    if ward[1].lower().find(name) != -1
                ]
            else:
                wards = [
                    {"id": ward[0], "name": ward[1]}
                    for ward in Wards(district_id).CHOICES
                ]
        cache.set(cache_key, wards)
        return wards

    @classmethod
    def get_ward(cls, district_id, ward_id):
        return Districts(district_id).DICT.get(ward_id)

    @classmethod
    def list(cls, user_id=None, text=None, **kwargs):

        queryset = Address.objects.all()

        if user_id:
            if isinstance(user_id, list):
                user_id = user_id[0]
            queryset = queryset.filter(user_id=user_id)
        if text:
            queryset = queryset.filter(detail__icontains=text)

        return queryset

    @classmethod
    def get(
        cls, address_id, user_id=None, raise_exception=True, **kwargs
    ) -> Union[Address, None]:
        try:
            address = Address.objects.get(id=address_id)
            if user_id and address.user_id != user_id:
                raise NotFound("Address is not found")
            return address
        except Exception:
            if raise_exception:
                raise NotFound("Address is not found")
            return None

    @classmethod
    def create(cls, user_id, city, district, ward, detail, **kwargs) -> Address:
        address = Address.objects.create(
            user_id=user_id, city=city, district=district, ward=ward, detail=detail
        )
        return address

    @classmethod
    def update(
        cls, instance: Address, validated: dict, partial=False, **kwargs
    ) -> Address:
        if partial:
            instance.city = validated.get("city", instance.city)
            instance.district = validated.get("district", instance.district)
            instance.ward = validated.get("ward", instance.ward)
            instance.detail = validated.get("detail", instance.detail)
        else:
            instance.city = validated.get("city")
            instance.district = validated.get("district")
            instance.ward = validated.get("ward")
            instance.detail = validated.get("detail")

        instance.save()
        return instance

    @classmethod
    def delete(cls, address_id, user_id=None, **kwargs) -> bool:
        address = cls.get(address_id, user_id)
        if address:
            address.delete()
        return True
