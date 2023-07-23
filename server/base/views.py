from django.http import JsonResponse

from rest_framework import permissions, authentication, status
from rest_framework.views import APIView
from rest_framework.response import Response
import os

from . import files_handler
from .serializers import FileMetaDataSerializer


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

    def post(self, request):
        for item in request.data:
            serializer = FileMetaDataSerializer(data=item   )
            if serializer.is_valid():
                return Response({"message" : "OK."},status=status.HTTP_200_OK)
        return Response({"message" : "Error"}, status=status.HTTP_400_BAD_REQUEST)
