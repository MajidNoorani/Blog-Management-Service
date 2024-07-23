from django.urls import path

from .views import (
    GoogleLoginApi,
    GoogleLoginRedirectApi,
)

urlpatterns = [
    path("callback/google",
         GoogleLoginApi.as_view(),
         name="callback-raw"),
    path("redirect/google",
         GoogleLoginRedirectApi.as_view(),
         name="redirect-raw"),
]
