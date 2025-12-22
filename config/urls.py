from django.conf import settings
from django.contrib import admin
from django.urls import path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    path(settings.ADMIN_URL, admin.site.urls),
    path("api/v1/schema", SpectacularAPIView.as_view(), name="schema"),
    path("api/v1/schema/redoc", SpectacularRedocView.as_view(), name="redoc"),
    path(
        "api/v1/schema/swagger-ui",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
]

admin.site.site_header = "Hober Bank Admin"
admin.site.site_title = "Hober Bank Admin Portal"
admin.site.index_title = "Welcome to Hosseini's Bank :) Admin Portal"

