from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token

from . import views

urlpatterns = [
    path("auth/", obtain_auth_token, name="auth"),
    path("getdir/", views.getdir, name="getdir"),
]
