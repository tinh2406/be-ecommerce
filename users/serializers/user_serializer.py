from django.core.validators import RegexValidator
from rest_framework.serializers import (
    BooleanField,
    CharField,
    ChoiceField,
    DateField,
    DateTimeField,
    EmailField,
    ModelSerializer,
    Serializer,
    ValidationError,
)

from core.utils import BaseQuerySerializer
from users.constants import Genders, Roles, UserOrderChoice
from users.models import User
from users.services import ESUserService, ProfileService, UserService


class RegisterSerializer(ModelSerializer):
    email = EmailField()
    password = CharField(validators=[])
    re_password = CharField()
    name = CharField()

    class Meta:
        model = User
        fields = ("email", "password", "re_password", "name")

    def validate(self, attrs):
        if attrs["password"] != attrs["re_password"]:
            raise ValidationError({"password": "Password does not match"}, 400)
        return attrs

    def create(self, validated_data):
        validated_data.pop("re_password")
        try:
            user = User.objects.create_user(**validated_data)
            ProfileService.create(user=user)
            ESUserService.index.delay(UserSerializer(user).data)
            return user
        except Exception as e:
            raise ValidationError(e, 400)


class LoginSerializer(Serializer):
    email = EmailField()
    password = CharField()


class ChangeEmailSerializer(Serializer):
    token = CharField()
    email = EmailField()

    def update(self, instance, validated_data):
        res = UserService.update_email(validated_data)
        return res


class UpdatePasswordSerializer(Serializer):
    old_password = CharField()
    new_password = CharField()
    re_new_password = CharField()

    def validate(self, attrs):
        if attrs["new_password"] != attrs["re_new_password"]:
            raise ValidationError({"new_password": "New password does not match"}, 400)
        return attrs

    def update(self, instance, validated_data):
        old_password = validated_data["old_password"]
        new_password = validated_data["new_password"]

        if not instance.check_password(old_password):
            raise ValidationError({"old_password": "Old password is incorrect"}, 400)

        instance.set_password(new_password)
        instance.save()
        return True


class UpdatePasswordWithTokenSerializer(Serializer):
    token = CharField()
    new_password = CharField()
    re_new_password = CharField()

    def validate(self, attrs):
        if attrs["new_password"] != attrs["re_new_password"]:
            raise ValidationError({"new_password": "New password does not match"}, 400)

        return attrs

    def update(self, instance, validated_data):
        res = UserService.update_password_with_token(validated_data)
        return res


class UpdateRoleSerializer(Serializer):
    role = ChoiceField(choices=Roles.CHOICES)

    def validate(self, attrs):
        if attrs["role"] == Roles.ADMIN:
            raise ValidationError("You cannot update to admin role")

        return attrs


class QueryUserSerializer(BaseQuerySerializer):
    role = ChoiceField(choices=Roles.CHOICES, allow_null=True, required=False)
    birthday = DateField(allow_null=True, required=False)
    birthday_from = DateField(allow_null=True, required=False)
    birthday_to = DateField(allow_null=True, required=False)
    gender = ChoiceField(choices=Genders.CHOICES, allow_null=True, required=False)
    is_deleted = BooleanField(allow_null=True, required=False)
    is_banned = BooleanField(allow_null=True, required=False)
    is_all = BooleanField(allow_null=True, required=False)
    delete_from = DateTimeField(allow_null=True, required=False)
    delete_to = DateTimeField(allow_null=True, required=False)
    banned_from = DateTimeField(allow_null=True, required=False)
    banned_to = DateTimeField(allow_null=True, required=False)
    created_from = DateTimeField(allow_null=True, required=False)
    created_to = DateTimeField(allow_null=True, required=False)

    # override
    order_by = ChoiceField(allow_null=True, required=False, choices=UserOrderChoice)


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"
        read_only_fields = ("id", "created_at", "deleted_at", "banned_at")

    name = CharField()
    birthday = DateField(allow_null=True)
    phone = CharField(
        max_length=11,
        allow_null=True,
        validators=[
            RegexValidator(r"^\d{10}$", message="Phone number must be 11 digits")
        ],
    )
    image = CharField(max_length=255, allow_null=True, allow_blank=True)
    gender = ChoiceField(choices=Genders.CHOICES, allow_null=True)

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
            "updated_at": instance.updated_at,
            "deleted_at": instance.deleted_at,
            "banned_at": instance.banned_at,
        }

    def update(self, instance, validated_data):
        partial = validated_data.pop("partial", False)
        UserService.update(instance, validated_data, partial=partial)
        ProfileService.update(instance.profile, validated_data, partial=partial)
        return instance
