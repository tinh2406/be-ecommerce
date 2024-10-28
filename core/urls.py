from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from django.urls import include, path

urlpatterns = [
    path("", lambda request: HttpResponse("Hello World")),
    path("api/v1/", include("users.urls")),
    path("api/v1/", include("products.urls")),
    path("api/v1/", include("crawlers.urls")),
    path("api/v1/", include("conversations.urls")),
] + static(settings.STATIC_URL)
