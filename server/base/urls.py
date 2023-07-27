from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token

from . import views

urlpatterns = [
    path("auth/", obtain_auth_token, name="auth"),
    path("check/", views.CheckMetaDataView.as_view(), name="check_files_metadata"),
    path("file/", views.FileView.as_view(), name="upload_files"),
    path(
        "file/<int:pk>/", views.FileView.as_view(), name="download_update_delete_files"
    ),
]
