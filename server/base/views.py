from django.http import FileResponse, HttpResponseServerError
from django.db import transaction

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser

from . import files_handler
from .serializers import FileMetaDataSerializer, FileSerializer
from .models import FileMetaData


class CheckMetaDataView(APIView):
    def get(self, request):
        current_user = request.user
        metadata_objects = FileMetaData.objects.filter(owner=current_user)
        serializer = FileMetaDataSerializer(metadata_objects, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class FileView(APIView):
    parser_classes = [MultiPartParser]

    def get(self, request, pk, format=None):
        try:
            file_metadata = FileMetaData.objects.get(pk=pk, owner=request.user)
        except FileMetaData.DoesNotExist:
            return Response(
                {"error": "File not found."}, status=status.HTTP_404_NOT_FOUND
            )
        file = files_handler.get_file_path(
            owner=request.user.username, path=file_metadata.path
        )

        return FileResponse(open(file, "rb"))

    def post(self, request, format=None):
        # get the file and remove it from the request
        file_data = {"file": request.data.get("file")}
        request.data.pop("file", None)
        # store the metadata and add the owner & updated_at fields
        json_data = request.data
        json_data.update({"owner": request.user.username})
        file_serializer = FileSerializer(data=file_data)
        metadata_serializer = FileMetaDataSerializer(data=json_data)
        with transaction.atomic():
            if file_serializer.is_valid() and metadata_serializer.is_valid():
                if FileMetaData.objects.filter(
                    path=metadata_serializer.validated_data["path"], owner=request.user
                ):
                    return Response(
                        {
                            "message": f'ERROR: file \'{metadata_serializer.validated_data["path"]}\' already exists!!'
                        }
                    )
                files_handler.upload_file(
                    owner=request.user.username,
                    path=metadata_serializer.validated_data["path"],
                    file=file_data["file"],
                )
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
                {"message": metadata_serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def put(self, request, pk, format=None):
        # get the file and remove it from the request
        file_data = {"file": request.data.get("file")}
        request.data.pop("file", None)
        # store the metadata and add the owner & updated_at fields
        json_data = request.data
        json_data.update({"owner": request.user.username})
        try:
            old_file_metadata = FileMetaData.objects.get(pk=pk, owner=request.user)
        except FileMetaData.DoesNotExist:
            return Response(
                {"error": "File not found."}, status=status.HTTP_404_NOT_FOUND
            )

        file_serializer = FileSerializer(data=file_data)
        metadata_serializer = FileMetaDataSerializer(old_file_metadata, data=json_data)
        with transaction.atomic():
            if file_serializer.is_valid() and metadata_serializer.is_valid():
                files_handler.update_file(
                    owner=request.user.username,
                    path=metadata_serializer.validated_data["path"],
                    file=file_data["file"],
                )
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

    def delete(self, request, pk, format=None):
        with transaction.atomic():
            try:
                file_metadata = FileMetaData.objects.get(pk=pk, owner=request.user)
            except FileMetaData.DoesNotExist:
                return Response(
                    {"error": "File not found."}, status=status.HTTP_404_NOT_FOUND
                )
            try:
                files_handler.delete_file(
                    owner=request.user.username, path=file_metadata.path
                )
                file_metadata.delete()
                return Response(
                    {"message": "File deleted successfully."}, status=status.HTTP_200_OK
                )
            except FileNotFoundError as e:
                return Response(
                    {"message": "ERROR: File not found!!!"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            except PermissionError as e:
                return Response(
                    {
                        "message": "ERROR: you don't have the permission to delete this file!!!"
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )
            except Exception as e:
                return HttpResponseServerError(
                    {"message": "ERROR: something went wrong..."}
                )
