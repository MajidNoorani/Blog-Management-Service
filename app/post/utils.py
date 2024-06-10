import os
from django.conf import settings
from urllib.parse import urljoin
from django.core.files.storage import FileSystemStorage
from django.core.files.base import ContentFile
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.crypto import get_random_string
from .serializers import FileUploadSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class CustomStorage(FileSystemStorage):
    """Custom storage for django_ckeditor_5 images."""
    def __init__(self,
                 location=settings.MEDIA_ROOT,
                 base_url=settings.MEDIA_URL
                 ):
        super().__init__(location, base_url)

    location = os.path.join(settings.MEDIA_ROOT, "")
    base_url = settings.MEDIA_URL

@csrf_exempt
def custom_upload_function(request):
    if request.method == 'POST' and request.FILES.get('upload'):
        upload = request.FILES['upload']

        # Generate a unique file name
        filename = get_random_string(length=32) + \
            os.path.splitext(upload.name)[1]
        # Path relative to MEDIA_ROOT
        file_path = os.path.join('uploads', 'contentFiles', filename)
        # Use custom storage to save the file
        custom_storage = CustomStorage()
        saved_path = custom_storage.save(file_path, ContentFile(upload.read()))

        # Construct the URL for the uploaded file
        file_url = custom_storage.url(saved_path)

        # Return the URL and success response
        return JsonResponse({
            'url': file_url,
            'uploaded': True,
        })

    return JsonResponse({'uploaded': False}, status=400)
