"""
Serializer Module responsible for validation ,serialize and deserialize of Data
"""



from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode as uid_decoder
from django.utils.encoding import force_text

from rest_framework import serializers
from rest_framework_jwt.settings import api_settings
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import (
    HyperlinkedModelSerializer
)
from drfjwtauthapi import settings


from sharedutils.emails import Email

from .utils import (
    SetPasswordForm,
    PasswordResetForm
)

from .models import (
    User,
)



# Get the UserModel

UserModel = get_user_model()

User = get_user_model()
jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
jwt_decode_handler = api_settings.JWT_DECODE_HANDLER
jwt_get_username_from_payload = api_settings.JWT_PAYLOAD_GET_USERNAME_HANDLER



class UserSerializer(HyperlinkedModelSerializer):
    """
     user writable  serializer
    """

    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class PasswordChangeSerializer(serializers.Serializer):
    """
    Utility used during password change process
    """
    old_password = serializers.CharField(max_length=128)
    new_password1 = serializers.CharField(max_length=128)
    new_password2 = serializers.CharField(max_length=128)

    set_password_form_class = SetPasswordForm

    def __init__(self, *args, **kwargs):
        """
        Setting for password related work
        :param args:
        :param kwargs:
        """
        self.old_password_field_enabled = getattr(
            settings, 'OLD_PASSWORD_FIELD_ENABLED', False
        )
        self.logout_on_password_change = getattr(
            settings, 'LOGOUT_ON_PASSWORD_CHANGE', False
        )
        super(PasswordChangeSerializer, self).__init__(*args, **kwargs)

        if not self.old_password_field_enabled:
            self.fields.pop('old_password')

        self.request = self.context.get('request')
        self.user = getattr(self.request, 'user', None)

    def validate_old_password(self, value):
        """
        Used if validate  old password
        :param value:
        :return:
        """
        invalid_password_conditions = (
            self.old_password_field_enabled,
            self.user,
            not self.user.check_password(value)
        )

        if all(invalid_password_conditions):
            raise serializers.ValidationError('Invalid password')
        return value

    def validate(self, attrs):
        """
        validate new password
        :param attrs:
        :return:
        """
        self.set_password_form = self.set_password_form_class(
            user=self.user, data=attrs
        )

        if not self.set_password_form.is_valid():
            raise serializers.ValidationError(self.set_password_form.errors)
        return attrs

    def save(self):
        """
        Change the password and send Password Change Email
        """
        self.set_password_form.save()
        if not self.logout_on_password_change:
            from django.contrib.auth import update_session_auth_hash
            update_session_auth_hash(self.request, self.user)
            email_sender = Email()
            email_sender.password_change_email(self.user)


class PasswordResetSerializer(serializers.Serializer):
    """
    Serializer for requesting a password reset e-mail.
    """
    email = serializers.EmailField()

    password_reset_form_class = PasswordResetForm

    def get_email_options(self):
        """Override this method to change default e-mail options"""
        return {}

    def validate_email(self, value):
        """
        Validate incoming email
        :param value:
        :return: return that email or rasie error
        """
        # Create PasswordResetForm with the serializer
        self.reset_form = self.password_reset_form_class(data=self.initial_data)
        if not self.reset_form.is_valid():
            raise serializers.ValidationError(self.reset_form.errors)

        return value

    def save(self):
        """
        this will set values to trigger email
        :return:
        """
        request = self.context.get('request')
        # Set some values to trigger the send_email method.
        opts = {
            'use_https': request.is_secure(),
            # 'from_email': getattr(settings, 'DEFAULT_FROM_EMAIL'),
            'request': request,
        }

        opts.update(self.get_email_options())
        self.reset_form.save(**opts)


class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    Serializer for requesting a password reset e-mail.
    """
    new_password1 = serializers.CharField(max_length=128)
    new_password2 = serializers.CharField(max_length=128)
    uid = serializers.CharField()
    token = serializers.CharField()

    set_password_form_class = SetPasswordForm

    def custom_validation(self, attrs):
        """

        :param attrs:
        :return:
        """
        pass

    def validate(self, attrs):
        """

        :param attrs:
        :return:
        """
        self._errors = {}

        # Decode the uidb64 to uid to get User object
        try:
            uid = force_text(uid_decoder(attrs['uid']))
            self.user = UserModel._default_manager.get(pk=uid)
        except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
            raise ValidationError({'uid': ['Invalid value']})

        self.custom_validation(attrs)
        # Construct SetPasswordForm instance
        self.set_password_form = self.set_password_form_class(
            user=self.user, data=attrs
        )
        if not self.set_password_form.is_valid():
            raise serializers.ValidationError(self.set_password_form.errors)
        if not default_token_generator.check_token(self.user, attrs['token']):
            raise ValidationError({'token': ['Invalid value']})

        return attrs

    def save(self):
        """

        :return:
        """
        return self.set_password_form.save()

# class CustomJWTSerializer(JSONWebTokenSerializer):
#     username_field = 'username'
#
#     def validate(self, attrs):
#
#         password = attrs.get("password")
#         user_obj = User.objects.filter(email=attrs.get("username")).first()
#         or User.objects.filter(
#             username=attrs.get("username")).first()
#         if user_obj is not None:
#             credentials = {
#                 'username': user_obj.username,
#                 'password': password
#             }
#             if all(credentials.values()):
#                 user = authenticate(**credentials)
#                 if user:
#                     if not user.is_active:
#                         msg = _('User account is disabled.')
#                         raise serializers.ValidationError(msg)
#
#                     payload = jwt_payload_handler(user)
#
#                     return {
#                         'token': jwt_encode_handler(payload),
#                         'user': user
#                     }
#                 else:
#                     msg = _('Unable to log in with provided credentials.')
#                     raise serializers.ValidationError(msg)
#
#             else:
#                 msg = _('Must include "{username_field}" and "password".')
#                 msg = msg.format(username_field=self.username_field)
#                 raise serializers.ValidationError(msg)
#
#         else:
#             msg = _('Account with this email/username does not exists')
#             raise serializers.ValidationError(msg)
