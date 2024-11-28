from users.domains import AddressDomain


class AddressService:

    @classmethod
    def create(cls, user_id, city, district, ward, detail):
        return AddressDomain.create(
            user_id=user_id, city=city, district=district, ward=ward, detail=detail
        )

    @classmethod
    def get(cls, address_id, user_id=None):
        return AddressDomain.get(address_id, user_id=user_id)

    @classmethod
    def list(cls, user_id=None, text=None):
        return AddressDomain.list(user_id=user_id, text=text)

    @classmethod
    def update(cls, address, update_data):
        return AddressDomain.update(address, update_data=update_data)

    @classmethod
    def delete(cls, address_id, user_id):
        return AddressDomain.delete(address_id, user_id)

    @classmethod
    def list_cities(cls, name=None):
        return AddressDomain.list_cities(name)

    @classmethod
    def list_districts(cls, city_id, name=None):
        return AddressDomain.list_districts(city_id, name)

    @classmethod
    def list_wards(cls, district_id, name=None):
        return AddressDomain.list_wards(district_id, name)
