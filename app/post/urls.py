"""
URL mappings for the recipe API.
"""
from django.urls import (
    path,
    include
)
from rest_framework.routers import DefaultRouter

from post import views

from post.utils import custom_upload_function, FileUploadView

router = DefaultRouter()
router.register('post_category', views.PostCategoryViewSet)
router.register('post', views.PostViewSet)
router.register('tags', views.TagViewSet)


app_name = 'post'

urlpatterns = [
    path('', include(router.urls)),
    path("upload/", custom_upload_function, name="custom_upload_file"),
]
