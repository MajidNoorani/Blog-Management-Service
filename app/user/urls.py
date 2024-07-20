from django.urls import path
from user import views

app_name = 'user'
urlpatterns = [
    path('create/', views.CreateUserView.as_view(), name='create'),
    path('token/', views.CreateTokenView.as_view(), name='token'),
    path('me/', views.ManageUserView.as_view(), name='me'),
    path('password-reset-request/',
         views.ResetPasswordRequestViewSet.as_view(),
         name='password-reset-request'),
    path('reset-password/',
         views.PasswordResetViewSet.as_view(),
         name='password-reset'),
    path('verification-email-request/',
         views.RequestVerificationEmailViewSet.as_view(),
         name='verification-email-request'),
    path('verify-email/',
         views.VerifyEmailViewSet.as_view(),
         name='verify-email'),
]
