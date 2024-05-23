"""
URL mappings for the recipe API.
"""
from django.urls import (
    path,
    include
)
from rest_framework.routers import DefaultRouter

from post import views

router = DefaultRouter()
router.register('post', views.PostCategoryViewSet)


app_name = 'post'

urlpatterns = [
    path('', include(router.urls))
]