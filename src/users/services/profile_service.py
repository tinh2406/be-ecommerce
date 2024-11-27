from users.models import Profile, User


class ProfileService:

    @classmethod
    def create(cls, user: User) -> Profile:
        return Profile.objects.create(user=user)

    @classmethod
    def update(cls, instance: Profile, update_data: dict, **kwargs) -> Profile:
        instance.phone = update_data.get("phone")
        instance.birthday = update_data.get("birthday")
        instance.gender = update_data.get("gender")
        instance.image = update_data.get("image")

        instance.save()
        return instance
