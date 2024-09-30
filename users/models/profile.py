from django.core.validators import RegexValidator
from django.db.models import Model, OneToOneField, CASCADE, DateField, CharField, ImageField, IntegerField

from users.constants import Genders
from users.managers import ProfileManager


class Profile(Model):
    user = OneToOneField('users.User', on_delete=CASCADE, related_name='profile', primary_key=True)

    birthday = DateField(null=True, blank=True)
    phone = CharField(max_length=11, null=True, blank=True, unique=True, validators=[
        RegexValidator(r'^\d{10}$', message='Phone number must be 11 digits')
    ])
    image = CharField(max_length=255, null=True, blank=True)
    gender = IntegerField(null=True, blank=True)

    objects = ProfileManager()

    class Meta:
        db_table = 'profiles'

    @property
    def get_gender(self):
        return Genders.DICT.get(self.gender)

