from rest_framework.serializers import Serializer, EmailField, CharField, \
    ValidationError, ModelSerializer

from users.models import User
from users.services import UserService


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


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'deleted_at', 'banned_at')

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