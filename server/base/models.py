from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class FileMetaData(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    hash = models.CharField(max_length=400)
    path = models.CharField(max_length=100)
    size = models.PositiveBigIntegerField()
