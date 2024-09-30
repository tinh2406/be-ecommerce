from users.models import Profile, User


class ProfileService:

    @classmethod
    def create(cls, user: User) -> Profile:
        return Profile.objects.create(user=user)




