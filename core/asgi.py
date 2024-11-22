import os
import sys

from django.core.asgi import get_asgi_application

filepath = os.path.abspath(__file__)

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(filepath))))
)


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")

application = get_asgi_application()
