from django.contrib.auth import login
from django.http.response import HttpResponseRedirect
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiParameter,
    OpenApiTypes
)
from .service import (
    GoogleRawLoginFlowService,
)
from core.models import User
from django.db.models.query import QuerySet
from rest_framework.authtoken.models import Token
# from datetime import timedelta
# from django.utils.timezone import now
from django.conf import settings
# from core.models import user_image_file_path
import urllib.request
import uuid
import os


def user_list(*, email=None) -> QuerySet[User]:
    qs = User.objects.all()
    return qs.filter(email=email)


class PublicApi(APIView):
    authentication_classes = ()
    permission_classes = ()


@extend_schema_view(
    get=extend_schema(
        description="""
        Redirects user to Google OAuth2 login page.
        By searching this url in browser, user will be redicrected
        to google login page.
        """
    )
)
class GoogleLoginRedirectApi(PublicApi):
    def get(self, request, *args, **kwargs):
        google_login_flow = GoogleRawLoginFlowService()

        authorization_url, state = google_login_flow.get_authorization_url()

        request.session["google_oauth2_state"] = state
        return HttpResponseRedirect(redirect_to=authorization_url)


@extend_schema_view(
    get=extend_schema(
        parameters=[
            OpenApiParameter(
                'state',
                OpenApiTypes.STR,
                description='State parameter received from Google OAuth2.'),
            OpenApiParameter(
                'code',
                OpenApiTypes.STR,
                description='Authorization code received from Google OAuth2.'),
            OpenApiParameter(
                'scope',
                OpenApiTypes.STR,
                description='Scopes requested from Google OAuth2.'),
        ],
    )
)
class GoogleLoginApi(PublicApi):
    class InputSerializer(serializers.Serializer):
        code = serializers.CharField(required=False)
        error = serializers.CharField(required=False)
        state = serializers.CharField(required=False)

    def get(self, request, *args, **kwargs):
        input_serializer = self.InputSerializer(data=request.GET)
        input_serializer.is_valid(raise_exception=True)

        validated_data = input_serializer.validated_data

        code = validated_data.get("code")
        error = validated_data.get("error")
        state = validated_data.get("state")

        if error is not None:
            return Response({"error": error},
                            status=status.HTTP_400_BAD_REQUEST)

        if code is None or state is None:
            return Response({"error": "Code and state are required."},
                            status=status.HTTP_400_BAD_REQUEST)

        # session_state = request.session.get("google_oauth2_state")

        # if session_state is None:
        #     return Response({"error": "CSRF check failed."},
        #                     status=status.HTTP_400_BAD_REQUEST)

        # del request.session["google_oauth2_state"]

        # if state != session_state:
        #     return Response({"error": "CSRF check failed."},
        #                     status=status.HTTP_400_BAD_REQUEST)

        google_login_flow = GoogleRawLoginFlowService()

        google_tokens = google_login_flow.get_tokens(code=code)

        id_token_decoded = google_tokens.decode_id_token()
        user_info = google_login_flow.get_user_info(
            google_tokens=google_tokens)

        user_email = id_token_decoded["email"]
        user, created = User.objects.get_or_create(email=user_email)
        print('picture: ', id_token_decoded.get("picture", ""))

        filename = f'{uuid.uuid4()}.jpg'
        image_file_path = os.path.join(settings.MEDIA_ROOT,
                                       'uploads',
                                       'users_images',
                                       filename)
        image_url = os.path.join('uploads', 'users_images', filename)

        if created:
            # downloading the image
            urllib.request.urlretrieve(id_token_decoded.get("picture", ""),
                                       image_file_path)
            user.name = id_token_decoded.get("name", "")
            user.image = image_url
            user.is_email_verified = True
        else:
            if not user.image:
                urllib.request.urlretrieve(id_token_decoded.get("picture", ""),
                                           image_file_path)
                user.image = image_url
                user.is_email_verified = True
            if not user.name:
                user.name = id_token_decoded.get("name", "")

        user.save()

        login(request, user)

        token, created = Token.objects.get_or_create(user=user)

        result = {
            "id_token_decoded": id_token_decoded,
            "user_info": user_info,
            "token": token.key,  # Return the token in the response
        }

        # response = redirect(settings.BASE_FRONTEND_URL)
        response = HttpResponseRedirect(redirect_to=settings.BASE_FRONTEND_URL)

        cookie_max_age = 3600  # 60 minutes
        response.set_cookie(
            key='auth_token',
            value=token.key,
            max_age=cookie_max_age,
            # httponly=True,
            secure=True,
            samesite='Lax',
            domain=f'.{settings.BASE_FRONTEND_URL.split("//")[1]}',
            # path='/'
        )

        return response
