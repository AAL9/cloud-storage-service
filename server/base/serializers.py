from django.contrib.auth.models import User

from rest_framework import serializers

from .models import FileMetaData


class FileMetaDataSerializer(serializers.ModelSerializer):
    owner = serializers.CharField(
        required=False
    )  # Add a write-only field for owner name

    class Meta:
        model = FileMetaData
        fields = ["owner", "name", "updated_at", "hash", "path", "size"]


class FileSerializer(serializers.Serializer):
    file = serializers.FileField()
