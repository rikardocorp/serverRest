# try:
#     from api.serializers import MethodSerializer
# except ImportError:
#     import sys
#     MethodSerializer = sys.modules[__package__ + '.MethodSerializer']
from rest_framework import serializers
from . import models
from api.models import Method
from django.contrib.auth.forms import PasswordResetForm
import os
from django.conf import settings

# from api.models import Method


class MethodSerializer(serializers.ModelSerializer):

    class Meta:
        model = Method
        fields = ['id', 'name', 'description', 'principal']


class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(style={'input_type': 'password'}, write_only=True, default=None)
    re_password = serializers.CharField(style={'input_type': 'password'}, write_only=True, default=None)
    method = MethodSerializer(many=False, read_only=True)
    method_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset=Method.objects.all(), source='method', default=None)

    class Meta:
        model = models.CustomUser
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'password', 're_password', 'is_superuser', 'is_active', 'is_principal', 'method', 'method_id', 'role', 'date_joined')
        # fields = '__all__'

    def validate(self, data):
        # user = self.context['request'].user
        print 'password'
        print data.get('password')
        print data.get('re_password')
        # print user
        pw = data.get('password')
        pw2 = data.get('re_password')
        if pw is not None and pw != pw2:
            raise serializers.ValidationError('Password must match')
        return data

    # def validate_username(self, value, *args, **kwargs):

    def validate_email(self, value, *args, **kwargs):
        print 'validate_email - instance'
        print self.instance
        username = None
        if self.instance is not None:
            username = self.instance.username

        email = value
        if email and models.CustomUser.objects.filter(email=email).exclude(username=username).count() > 0:
            raise serializers.ValidationError(u'This email address is already registered.')
        return str(email).lower()

    def validate_is_active(self, value):
        print 'IS ACTIVE', value

        superuser = None
        if self.instance is not None:
            superuser = self.instance.is_superuser

        if value is False and superuser:
            if models.CustomUser.objects.filter(is_superuser=True, is_active=True).count() <= 1:
                raise serializers.ValidationError(u'Debe existir al menos una cuenta de administrador activa.')
        return value

    # def update(self, instance, validated_data):
    #     print 'CustomUserSerializer'
    #     print instance
    #     return instance


class PasswordResetDefaultSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password_reset_form_class = PasswordResetForm

    def validate_email(self, value):
        self.reset_form = self.password_reset_form_class(data=self.initial_data)
        if not self.reset_form.is_valid():
            raise serializers.ValidationError(_('Error'))

        if not models.CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError(_('Invalid e-mail address'))
        return value

    def save(self):
        request = self.context.get('request')
        print 'SEND EMAIL'
        # print request.query_params.get('domain')

        hostname = request.META['HTTP_HOST']
        hostname_origin = request.META.get('HTTP_ORIGIN')
        print hostname
        print hostname_origin
        # print request.token
        # print list(request)
        opts = {
            'domain_override': hostname_origin,
            'use_https': request.is_secure(),
            'from_email': getattr(settings, 'DEFAULT_FROM_EMAIL'),
            'html_email_template_name': os.path.join(settings.BASE_DIR, 'users/templates/reset_password.html'),
            'request': request,
        }
        self.reset_form.save(**opts)
