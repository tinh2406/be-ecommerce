from users.services import AddressService


class AddressDomain:

    @classmethod
    def create(cls, user_id, city, district, ward, detail):
        return AddressService.create(
            user_id=user_id, city=city, district=district, ward=ward, detail=detail
        )

    @classmethod
    def get(cls, address_id, user_id=None):
        return AddressService.get(address_id, user_id=user_id)

    @classmethod
    def list(cls, user_id=None, text=None):
        return AddressService.list(user_id=user_id, text=text)

    @classmethod
    def update(cls, address, update_data):
        return AddressService.update(address, update_data=update_data)

    @classmethod
    def delete(cls, address_id, user_id):
        return AddressService.delete(address_id, user_id)

    @classmethod
    def list_cities(cls, name=None):
        return AddressService.list_cities(name)

    @classmethod
    def list_districts(cls, city_id, name=None):
        return AddressService.list_districts(city_id, name)

    @classmethod
    def list_wards(cls, district_id, name=None):
        return AddressService.list_wards(district_id, name)
