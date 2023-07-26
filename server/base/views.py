from django.http import JsonResponse

from rest_framework import permissions, authentication, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser

import os
from datetime import datetime

from . import files_handler
from .serializers import FileMetaDataSerializer, FileSerializer
from .models import FileMetaData


class CheckMetaDataView(APIView):
    authentication_classes = [
        authentication.SessionAuthentication,
        authentication.TokenAuthentication,
    ]
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
    ]

    def get(self, request):
        current_user = request.user
        metadata_objects = FileMetaData.objects.filter(owner=current_user)
        serializer = FileMetaDataSerializer(metadata_objects, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class FileView(APIView):
    parser_classes = [MultiPartParser]

    authentication_classes = [
        authentication.SessionAuthentication,
        authentication.TokenAuthentication,
    ]
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    def post(self, request, format=None):
        # get the file and remove it from the request
        file_data = {"file": request.data.get("file")}
        request.data.pop("file", None)
        # store the metadata and add the owner & updated_at fields
        json_data = request.data
        json_data.update(
            {"owner": str(request.user)}
        )
        file_serializer = FileSerializer(data=file_data)
        metadata_serializer = FileMetaDataSerializer(data=json_data)
        if file_serializer.is_valid() and metadata_serializer.is_valid():
            if FileMetaData.objects.filter(
                path=metadata_serializer.validated_data["path"], owner=request.user
            ):
                return Response(
                    {
                        "message": f'ERROR: file \'{metadata_serializer.validated_data["path"]}\' already exists!!'
                    }
                )
            storage_folder_path = os.path.abspath(
                os.path.join(__file__, "..", "..", "..", "cloud_storage")
            )
            file_path = os.path.join(
                storage_folder_path, metadata_serializer.validated_data["owner"]
            )
            file_path = file_path + str(metadata_serializer.validated_data["path"])
            dir_path = os.path.dirname(file_path)
            os.makedirs(dir_path, exist_ok=True)
            with open(file_path, "wb+") as destination_file:
                for chunk in file_data["file"].chunks():
                    destination_file.write(chunk)
            metadata_serializer.validated_data["owner"] = request.user
            metadata_serializer.save()
            content = {
                "message": f'File \'{metadata_serializer.validated_data["path"]}\' uploaded successfully.',
                "metadata": metadata_serializer.data,
            }
            return Response(
                content,
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {"message": metadata_serializer.errors}, status=status.HTTP_400_BAD_REQUEST
        )

    def put(self, request, format=None):
        # get the file and remove it from the request
        file_data = {"file": request.data.get("file")}
        request.data.pop("file", None)
        # store the metadata and add the owner & updated_at fields
        json_data = request.data
        json_data.update(
            {"owner": str(request.user)}
        )
        try:
            old_file_metadata = FileMetaData.objects.get(
                path=request.data["path"], owner=request.user
            )
        except FileMetaData.DoesNotExist:
            return Response(
                {"error": "File metadata not found."}, status=status.HTTP_404_NOT_FOUND
            )

        file_serializer = FileSerializer(data=file_data)
        metadata_serializer = FileMetaDataSerializer(old_file_metadata, data=json_data)
        if file_serializer.is_valid() and metadata_serializer.is_valid():
            storage_folder_path = os.path.abspath(
                os.path.join(__file__, "..", "..", "..", "cloud_storage")
            )
            file_path = os.path.join(
                storage_folder_path, metadata_serializer.validated_data["owner"]
            )
            file_path = file_path + str(metadata_serializer.validated_data["path"])
            dir_path = os.path.dirname(file_path)
            os.makedirs(dir_path, exist_ok=True)
            with open(file_path, "wb+") as destination_file:
                for chunk in file_data["file"].chunks():
                    destination_file.write(chunk)
            metadata_serializer.validated_data["owner"] = request.user
            metadata_serializer.save()
            content = {
                "message": f'File \'{metadata_serializer.validated_data["path"]}\' updated successfully.',
                "metadata": metadata_serializer.data,
            }
            return Response(
                content,
                status=status.HTTP_201_CREATED,
            )
        return Response(
            metadata_serializer.errors, status=status.HTTP_400_BAD_REQUEST
        )
