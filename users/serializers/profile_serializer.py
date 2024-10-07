from rest_framework.serializers import ModelSerializer

from users.models import Profile


class ProfileSerializer(ModelSerializer):
    class Meta:
        model = Profile
        fields = "__all__"

        read_only_fields = ("user", "created_at", "deleted_at")

    def validate(self, attrs):
        if "birthday" in attrs and attrs["birthday"] > attrs["created_at"]:
            raise ValueError("Birthday must be less than created_at")

        return attrs
