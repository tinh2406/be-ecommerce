from rest_framework.serializers import Serializer, EmailField, CharField, ValidationError

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
