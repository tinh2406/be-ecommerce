from django.core.validators import RegexValidator
from django.db.models import (
    CASCADE,
    CharField,
    DateField,
    IntegerField,
    Model,
    OneToOneField,
)

from users.constants import Genders


class Profile(Model):
    user = OneToOneField(
        "users.User", on_delete=CASCADE, related_name="profile", primary_key=True
    )

    birthday = DateField(null=True, blank=True)
    phone = CharField(
        max_length=11,
        null=True,
        blank=True,
        unique=True,
        validators=[
            RegexValidator(r"^\d{10}$", message="Phone number must be 11 digits")
        ],
    )
    image = CharField(max_length=255, null=True, blank=True)
    gender = IntegerField(null=True, blank=True)

    class Meta:
        db_table = "profiles"

    @property
    def gender_name(self):
        return Genders.DICT.get(self.gender)
