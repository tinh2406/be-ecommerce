from rest_framework.serializers import Serializer, EmailField, CharField, \
    ValidationError, ModelSerializer, DateField, ChoiceField
from django.core.validators import RegexValidator

from users.models import User
from users.services import UserService, ProfileService
from users.constants import Genders, Roles


class RegisterSerializer(Serializer):
    email = EmailField()
    password = CharField(validators=[

    ])
    re_password = CharField()
    name = CharField()

    def create(self, validated_data):
        return UserService.create(validated_data)

    def validate(self, attrs):
        user = UserService.get_by_email(attrs['email'], raise_exception=False)
        if user:
            raise ValidationError({"email": "Email already exists"}, 400)
        if attrs['password'] != attrs['re_password']:
            raise ValidationError({"password": "Password does not match"}, 400)
        return attrs

class LoginSerializer(Serializer):
    email = EmailField()
    password = CharField()

    def create(self, validated_data):
        email = validated_data.get('email')
        password = validated_data.get('password')
        return UserService.login(email, password)

class ChangeEmailSerializer(Serializer):
    token = CharField()
    email = EmailField()

    def validate(self, attrs):
        user = UserService.get_by_email(attrs['email'], raise_exception=False)
        if user:
            raise ValidationError({"email": "Email already exists"}, 400)
        return attrs

class UpdatePasswordSerializer(Serializer):
    old_password = CharField()
    new_password = CharField()
    re_new_password = CharField()

    def validate(self, attrs):
        if attrs['new_password'] != attrs['re_new_password']:
            raise ValidationError({"new_password": "New password does not match"}, 400)
        return attrs

    def update(self, instance, validated_data):
        res = UserService.update_password(instance, validated_data)
        return res

class UpdatePasswordWithTokenSerializer(Serializer):
    token = CharField()
    new_password = CharField()
    re_new_password = CharField()

    def validate(self, attrs):
        if attrs['new_password'] != attrs['re_new_password']:
            raise ValidationError({"new_password": "New password does not match"}, 400)

        return attrs

    def update(self, instance, validated_data):
        res = UserService.update_password_with_token(validated_data)
        return res

class UpdateRoleSerializer(Serializer):
    role = ChoiceField(choices=Roles.CHOICES)

    def validate(self, attrs):
        if attrs['role'] == Roles.ADMIN:
            raise ValidationError('You cannot update to admin role')

        return attrs

class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'deleted_at', 'banned_at')

    name = CharField()
    birthday = DateField(allow_null=True)
    phone = CharField(max_length=11, allow_null=True, validators=[
        RegexValidator(r'^\d{10}$', message='Phone number must be 11 digits')
    ])
    image = CharField(max_length=255, allow_null=True)
    gender = ChoiceField(choices=Genders.CHOICES, allow_null=True)

    def to_representation(self, instance):
        return {
            'id': instance.id,
            'name': instance.name,
            'email': instance.email,
            'birthday': instance.profile.birthday,
            'phone': instance.profile.phone,
            'gender': instance.profile.get_gender,
            'image': instance.profile.image,
            'role': instance.get_role,
            'created_at': instance.created_at,
            'deleted_at': instance.deleted_at,
            'banned_at': instance.banned_at
        }

    def update(self, instance, validated_data):
        partial = validated_data.pop('partial', False)
        UserService.update(instance, validated_data, partial=partial)
        ProfileService.update(instance.profile, validated_data, partial=partial)
        return instance