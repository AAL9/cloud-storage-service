from django.contrib.auth.models import User

from rest_framework import serializers

from .models import FileMetaData


class FileMetaDataSerializer(serializers.ModelSerializer):
    owner = serializers.CharField(
        required=False
    )  # Add a write-only field for owner name
    created_at = serializers.ReadOnlyField()
    updated_at = serializers.ReadOnlyField()
    id = serializers.ReadOnlyField()

    class Meta:
        model = FileMetaData
        fields = [
            "id",
            "owner",
            "name",
            "created_at",
            "updated_at",
            "hash",
            "path",
            "size",
        ]


class FileSerializer(serializers.Serializer):
    file = serializers.FileField(allow_empty_file=True)
