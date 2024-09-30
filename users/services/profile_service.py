from users.document import UserDocument
from users.models import Profile, User


class ProfileService:

    @classmethod
    def create(cls, user: User) -> Profile:
        return Profile.objects.create(user=user)

    @classmethod
    def update(cls, instance: Profile, data: dict, partial=False, **kwargs) -> Profile:
        if partial:
            instance.phone = data.get('phone', instance.phone)
            instance.birthday = data.get('birthday', instance.birthday)
            instance.gender = data.get('gender', instance.gender)
            instance.image = data.get('image', instance.image)
        else:
            instance.phone = data.get('phone')
            instance.birthday = data.get('birthday')
            instance.gender = data.get('gender')
            instance.image = data.get('image')
        instance.save()
        user_doc = UserDocument.get(id=instance.user.id)
        user_doc.update(
            phone=instance.phone,
            birthday=instance.birthday,
            gender=instance.gender,
        )
        return instance


