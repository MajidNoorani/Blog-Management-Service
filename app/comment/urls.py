"""
URL mappings for the organization API.
"""
from django.urls import (
    path,
    include
)
from rest_framework.routers import DefaultRouter

from comment import views

router = DefaultRouter()
router.register('Comment', views.CommentViewSet)
router.register('commentReaction', views.CommentReactionViewSet)


app_name = 'comment'

urlpatterns = [
    path('', include(router.urls))
]
