from django.urls import path
from . import views
urlpatterns = [
    path('getdir/', views.getdir, name="getdir" ),
]
