from rest_framework import generics, authentication, permissions
from .serializers import (
    UserSerializer,
    AuthTokenSerializer,
    ResetPasswordRequestSerializer,
    PasswordResetSerializer,
    RequestVerificationEmailSerializer,
    VerifyEmailSerializer
)
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings # noqa
from rest_framework.parsers import MultiPartParser

from rest_framework import status
from rest_framework.response import Response
from user import services


class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system."""
    serializer_class = UserSerializer
    parser_classes = [MultiPartParser]

    def perform_create(self, serializer):
        user = serializer.save()
        services.send_email_verification(user)


class CreateTokenView(ObtainAuthToken):
    """Create a new auth token for user."""
    serializer_class = AuthTokenSerializer
    # It seems that the next line is not needed
    # i have commented it and it works
    # renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manage the authenticated user."""
    serializer_class = UserSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class ResetPasswordRequestViewSet(generics.CreateAPIView):
    """Request password reset by sending an email with the reset token."""
    serializer_class = ResetPasswordRequestSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {'detail': 'Password reset email has been sent.'},
            status=status.HTTP_200_OK)


class PasswordResetViewSet(generics.CreateAPIView, generics.GenericAPIView):
    """Reset password using the token sent via email."""
    serializer_class = PasswordResetSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {'detail': 'Password has been reset successfully.'},
            status=status.HTTP_200_OK)


class RequestVerificationEmailViewSet(generics.CreateAPIView):
    """Request password reset by sending an email with the reset token."""
    serializer_class = RequestVerificationEmailSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {'detail': 'Verification email has been sent.'},
            status=status.HTTP_200_OK)


class VerifyEmailViewSet(generics.CreateAPIView, generics.GenericAPIView):
    """Reset password using the token sent via email."""
    serializer_class = VerifyEmailSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {'detail': 'Email has been verified successfully.'},
            status=status.HTTP_200_OK)
