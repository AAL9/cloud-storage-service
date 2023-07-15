from django.http import HttpResponse
from django.shortcuts import render
import os
from . import files_handler
# Create your views here.

def getdir(request):
    current_dir = os.getcwd()
    parent_dir = os.path.dirname(current_dir)
    target_dir = os.path.join(parent_dir, 'cloud_storage')
    if os.path.exists(target_dir):
        list = files_handler.get_all_files_dirs(target_dir)
        print("List of the files: ",list)
    else:
        # Handle the case when the target directory doesn't exist
        print(f"ERROR: Target directory does not exist: {target_dir}")
    return HttpResponse("Hi")
