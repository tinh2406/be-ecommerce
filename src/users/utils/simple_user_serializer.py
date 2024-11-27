from rest_framework.serializers import ModelSerializer

from users.models import User


class SimpleUserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"

    def to_representation(self, instance):
        return {
            "id": instance.id,
            "name": instance.name,
            "email": instance.email,
            "birthday": instance.profile.birthday,
            "phone": instance.profile.phone,
            "gender": instance.profile.gender,
            "gender_name": instance.profile.gender_name,
            "image": instance.profile.image,
            "role": instance.role,
            "role_name": instance.role_name,
            "created_at": instance.created_at,
            "deleted_at": instance.deleted_at,
            "banned_at": instance.banned_at,
        }
