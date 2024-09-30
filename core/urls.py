from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from django.urls import path

urlpatterns = [
    path("", lambda request: HttpResponse("Hello World")),
] + static(settings.STATIC_URL)
