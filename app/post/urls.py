"""
URL mappings for the recipe API.
"""
from django.urls import (
    path,
    include
)
from rest_framework.routers import DefaultRouter

from post import views

from post.utils import custom_upload_function
from post.views import FileUploadViewSet

router = DefaultRouter()
router.register('post_category', views.PostCategoryViewSet)
router.register('post', views.PostViewSet)
router.register('file-upload', FileUploadViewSet, basename='file-upload')
router.register('tags', views.TagViewSet)
router.register('postRate', views.PostRateViewSet)


app_name = 'post'

urlpatterns = [
    path('', include(router.urls)),
    path('api/upload-file/', custom_upload_function, name='custom_upload_file')
    # path("upload/", custom_upload_function, name="custom_upload_file"),
    # path("upload/", FileUploadViewSet.as_view(), name="custom_upload_file"),
]
