from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from django.urls import include, path

urlpatterns = [
    path("", lambda request: HttpResponse("Hello World")),
    path("api/v1/", include("users.urls")),
    path("api/v1/", include("items.urls")),
] + static(settings.STATIC_URL)
