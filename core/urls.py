from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from django.urls import path, include

urlpatterns = [
    path("", lambda request: HttpResponse("Hello World")),
    path('api/v1/', include('users.urls')),
] + static(settings.STATIC_URL)
