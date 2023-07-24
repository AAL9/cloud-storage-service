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


# @login_required
def getdir(request):
    current_dir = os.getcwd()
    parent_dir = os.path.dirname(current_dir)
    target_dir = os.path.join(parent_dir, "cloud_storage")
    list = []
    if os.path.exists(target_dir):
        list = files_handler.get_all_files_dirs(target_dir)
    else:
        # Handle the case when the target directory doesn't exist
        pass
    context = {"list": list}
    return JsonResponse(context)


class CheckMetaDataView(APIView):
    authentication_classes = [
        authentication.SessionAuthentication,
        authentication.TokenAuthentication,
    ]
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
    ]

    def get(self, request):
        # Assuming the user is authenticated, you can get the current user instance
        current_user = request.user
        print(current_user)
        # Fetch all metadata objects related to the current user from the database
        metadata_objects = FileMetaData.objects.filter(owner=current_user)
        print(metadata_objects)
        # Serialize the metadata objects
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
            {"owner": str(request.user), "updated_at": datetime.utcnow().isoformat()}
        )
        file_serializer = FileSerializer(data=file_data)
        metadata_serializer = FileMetaDataSerializer(data=json_data)
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

            metadata_serializer.save()
            return Response(
                {"message": "File and metadata uploaded successfully."},
                status=status.HTTP_201_CREATED,
            )
        return Response(
            metadata_serializer.error_messages, status=status.HTTP_400_BAD_REQUEST
        )
