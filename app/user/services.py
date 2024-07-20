# services.py
import random
from django.core.mail import send_mail
from django.conf import settings
from itsdangerous import URLSafeTimedSerializer
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.exceptions import ValidationError


def generate_email_verification_token(email):
    serializer = URLSafeTimedSerializer(settings.EMAIL_SECRET_KEY)
    token = serializer.dumps(
        {'email': email, 'salt': random.randrange(start=int(1e10),
                                                  stop=int(1e18),
                                                  step=1)}
    )
    return token


def validate_email_verification_token(token):
    serializer = URLSafeTimedSerializer(settings.EMAIL_SECRET_KEY)
    try:
        # Token is valid for 30 minutes
        data = serializer.loads(token, max_age=1800)
        return data
    except Exception:
        raise ValidationError("The request is not valid. Try again!")


def send_email_verification(user):
    token = generate_email_verification_token(user.email)
    verification_url = \
        f"{settings.BASE_FRONTEND_URL}/verify_email?&token={token}"
    html_message = render_to_string(
        'email/email_validation_template.html',
        {
            'reset_url': verification_url,
            'name': user.name,
            'homepage': settings.BASE_FRONTEND_URL,
            'backend_url': settings.BASE_BACKEND_URL,
            'support_mail_address': settings.EMAIL_HOST_USER
        }
    )
    plain_message = strip_tags(html_message)
    send_mail(
        subject='Email Verification',
        message=plain_message,
        html_message=html_message,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[user.email],
        fail_silently=False,
    )


def generate_temporary_code(user):
    user.temp_reset_password_code = random.randrange(start=int(1e10),
                                                     stop=int(1e18),
                                                     step=1)
    user.save()


def generate_password_reset_token(email, code):
    serializer = URLSafeTimedSerializer(settings.EMAIL_SECRET_KEY)
    token = serializer.dumps({'email': email, 'code': code})
    return token


def validate_password_reset_token(token):
    serializer = URLSafeTimedSerializer(settings.EMAIL_SECRET_KEY)
    try:
        # Token is valid for 30 minutes
        data = serializer.loads(token, max_age=1800)
        return data
    except Exception:
        raise ValidationError("The request is not valid. Try again!")


def send_password_reset_email(user):
    generate_temporary_code(user)
    token = generate_password_reset_token(user.email,
                                          user.temp_reset_password_code)
    reset_url = f"{settings.BASE_FRONTEND_URL}/reset-password?&token={token}"
    html_message = render_to_string(
        'email/forget_password_template.html',
        {
            'reset_url': reset_url,
            'name': user.name,
            'homepage': settings.BASE_FRONTEND_URL,
            'backend_url': settings.BASE_BACKEND_URL,
            'support_mail_address': settings.EMAIL_HOST_USER
        }
    )
    plain_message = strip_tags(html_message)
    send_mail(
        subject='Password Reset Request',
        message=plain_message,
        html_message=html_message,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[user.email],
        fail_silently=False,
    )
