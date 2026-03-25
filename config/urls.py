from django.contrib import admin
from django.urls import path, include
from drf_yasg.views import get_schema_view

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("users.urls", namespace="users")),
]
