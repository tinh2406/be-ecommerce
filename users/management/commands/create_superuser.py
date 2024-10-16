from django.core.management import BaseCommand

from users.models import Profile, User


class Command(BaseCommand):
    help = "Create a superuser"

    def add_arguments(self, parser):
        parser.add_argument("email", type=str, help="Email")
        parser.add_argument("password", type=str, help="Password")
        parser.add_argument("name", type=str, help="Name")

    def handle(self, *args, **options):
        email = options["email"]
        password = options["password"]
        name = options["name"]

        assert email, "Email is required"
        assert password, "Password is required"
        assert name, "Name is required"

        user = User.objects.create_user(
            email=email,
            password=password,
            name=name,
        )
        user.is_superuser = True
        user.save()
        Profile.objects.create(user=user)

        self.stdout.write(self.style.SUCCESS("Superuser created successfully"))
