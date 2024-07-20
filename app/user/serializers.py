from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import gettext as _
from rest_framework import serializers
from django.utils import timezone
from user import services


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object"""

    class Meta:
        model = get_user_model()
        fields = ['email', 'password', 'name', 'image']
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}

    def create(self, validated_data):
        """Create and return a user with encrypted password"""
        user = get_user_model().objects.create_user(**validated_data)
        services.send_email_verification(user)
        return user

    def update(self, instance, validated_data):
        """Update and return user."""
        password = validated_data.pop('password', None)
        user = super().update(instance=instance, validated_data=validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user


class AuthTokenSerializer(serializers.Serializer):
    """Validate and authenticate the user"""

    email = serializers.EmailField()
    password = serializers.CharField(style={'input_type': 'password'},
                                     trim_whitespace=False)

    def validate(self, attrs):
        """Validate and authenticate the user"""
        email = attrs.get('email')
        password = attrs.get('password')
        user = authenticate(request=self.context.get('request'),
                            username=email, password=password)
        if not user:
            msg = _('Unable to authenticate with provided credentials!')
            raise serializers.ValidationError(msg, code='authorization')

        if not user.is_activated:
            msg = _('Your account has been deactivated!')
            raise serializers.ValidationError(msg, code='authorization')

        if not user.is_email_verified:
            msg = _('Your account is not validated!')
            raise serializers.ValidationError(msg, code='authorization')

        user.last_login = timezone.now()
        user.save()
        attrs['user'] = user
        return attrs


class ResetPasswordRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            get_user_model().objects.get(email=value)
        except get_user_model().DoesNotExist:
            raise serializers.ValidationError(
                'User with this email does not exist.')
        return value

    def save(self):
        email = self.validated_data['email']
        user = get_user_model().objects.get(email=email)
        services.send_password_reset_email(user)


class PasswordResetSerializer(serializers.Serializer):
    token = serializers.CharField(help_text="Password reset token")
    new_password = serializers.CharField(write_only=True,
                                         help_text="New password")

    def validate(self, attrs):
        token = attrs.get('token')
        data = services.validate_password_reset_token(token)
        try:
            user = get_user_model().objects.get(email=data.get('email'))
        except get_user_model().DoesNotExist:
            raise serializers.ValidationError(
                'User with this email does not exist.')
        print(user.temp_reset_password_code, data.get('code'))
        if user.temp_reset_password_code != data.get('code'):
            raise serializers.ValidationError('Invalid or expired token.')

        return attrs

    def save(self):
        email = services.validate_password_reset_token(
            self.validated_data['token'])['email']
        new_password = self.validated_data['new_password']
        user = get_user_model().objects.get(email=email)
        user.set_password(new_password)
        user.temporary_code = None
        user.save()


class RequestVerificationEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            get_user_model().objects.get(email=value)
        except get_user_model().DoesNotExist:
            raise serializers.ValidationError(
                'User with this email does not exist! Try to sign-up first.')
        return value

    def save(self):
        email = self.validated_data['email']
        user = get_user_model().objects.get(email=email)
        if not user.is_email_verified:
            services.send_email_verification(user)
        else:
            raise serializers.ValidationError(
                'This email has already verified.')


class VerifyEmailSerializer(serializers.Serializer):
    token = serializers.CharField(help_text="Email Verification Token")

    def validate(self, attrs):
        token = attrs.get('token')
        data = services.validate_email_verification_token(token)
        try:
            get_user_model().objects.get(email=data.get('email'))
        except get_user_model().DoesNotExist:
            raise serializers.ValidationError(
                'User with this email does not exist.')
        return attrs

    def save(self):
        email = services.validate_email_verification_token(
            self.validated_data['token'])['email']
        user = get_user_model().objects.get(email=email)
        user.is_email_verified = True
        user.save()
