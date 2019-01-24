# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db.models import Q

from django.shortcuts import render

# Create your views here.

import os
from django.conf import settings
from rest_framework import generics, viewsets, status, permissions
from rest_framework.response import Response
from . import models
from . import serializers
from api.serializers import UserProfileSerializer
from api.models import UserProfile
from api.permissions import IsAdminLocal, IsAdminUserLocal
from django.template.loader import render_to_string, get_template
from django.template import Context
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate

REGISTER = 'REGISTER'
CHANGE_PASSWORD = 'CHANGE_PASSWORD'
CHANGE_EMAIL = 'CHANGE_EMAIL'
CHANGE_EMAIL_OLD = 'CHANGE_EMAIL_OLD'


def local_send_email(type, email, data):
    template_name = ''
    subject = ''
    if type == REGISTER:
        template_name = 'users/templates/register_user.html'
        subject = "Usuario Registrado"
    elif type == CHANGE_PASSWORD:
        template_name = 'users/templates/change_password.html'
        subject = "Cambio de contraseña"
    elif type == CHANGE_EMAIL:
        template_name = 'users/templates/change_email.html'
        subject = "Email Vinculado"
    elif type == CHANGE_EMAIL_OLD:
        template_name = 'users/templates/change_email_old.html'
        subject = "Email Desvinculado"

    to = [email]
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL')

    message_text = ''
    message_html = render_to_string(os.path.join(settings.BASE_DIR, template_name), data)
    # msg = EmailMessage(subject, message_text, to=to, from_email=from_email, message_html=message_html)
    # msg.content_subtype = 'html'
    # msg.send()
    send_mail(subject, message_text, from_email, to, html_message=message_html)


class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = models.CustomUser.objects.all()
    serializer_class = serializers.CustomUserSerializer
    permission_classes = [IsAdminUserLocal]

    def get_queryset(self):
        queryset = models.CustomUser.objects.all()
        return queryset

    def update(self, request, *args, **kwargs):
        print 'UPDATE'
        pass

    def partial_update(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        data = request.data
        # print data
        username = None
        if 'username' in request.data:
            username = data.pop('username')

        type = None
        if 'type' in request.data:
            type = data.pop('type')

        if 'role' in request.data:
            role = data.get('role')
            if isinstance(role, list):
                data['role'] = ','.join(role)

        # print 'New Data'
        # print pk
        # print data
        # print data['email']
        # newEmail = data['email']
        # print data['method']
        instance = self.queryset.get(pk=pk)
        # print 'instance'
        # print instance.email
        # oldEmail = instance.email
        # print instance
        # print 'USER UPDATE PRE'
        serializer = self.serializer_class(instance=instance, data=data, partial=True)
        # print 'USER UPDATE PRE POST'
        if serializer.is_valid():
            # print 'USER UPDATE POST'
            if type is None:
                newEmail = str(data['email'])
                oldEmail = str(instance.email)
                print 'UPDATED!'
                serializer.save()
                custom_user = instance
                if newEmail.upper() != oldEmail.upper():
                    hostname_origin = request.META.get('HTTP_ORIGIN')
                    data_email_new = {
                        'fullname': str(custom_user.first_name) + ' ' + str(custom_user.last_name),
                        'username': str(custom_user.username),
                        'email': str(custom_user.email),
                        'is_superuser': custom_user.is_superuser,
                        'hostname': hostname_origin,
                        'is_active': custom_user.is_active
                    }
                    local_send_email(CHANGE_EMAIL, custom_user.email, data_email_new)
                    data_email_old = {
                        'username': str(custom_user.username),
                        'email': str(oldEmail),
                        'hostname': hostname_origin,
                    }
                    local_send_email(CHANGE_EMAIL_OLD, oldEmail, data_email_old)
            else:
                # print 'UPDATED PASSWORD!'
                password = data.get('password')
                # print password
                # print make_password(password)
                # print '---------------------'
                custom_user = instance
                # print custom_user.password
                # print '---------------------'

                old_password = None
                if 'oldPassword' in data:
                    old_password = data.get('oldPassword')

                # print 'oldPassword: ' + str(old_password)

                if old_password is None or authenticate(username=username, password=old_password) is not None:
                    instance.set_password(password)
                    instance.save()

                    hostname_origin = request.META.get('HTTP_ORIGIN')
                    data_email_new = {
                        'fullname': str(custom_user.first_name) + ' ' + str(custom_user.last_name),
                        'username': str(custom_user.username),
                        'email': str(custom_user.email),
                        'is_superuser': custom_user.is_superuser,
                        'hostname': hostname_origin,
                        'password': password,
                        'is_active': custom_user.is_active
                    }
                    local_send_email(CHANGE_PASSWORD, custom_user.email, data_email_new)
                else:
                    return Response('La contraseña es incorrecta.', status=status.HTTP_400_BAD_REQUEST)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request, *args, **kwargs):
        data = request.data
        role = None
        if 'role' in request.data:
            role = data.pop('role')
            if isinstance(role, list):
                role = ','.join(role)

        print 'ROLE'
        print role
        if 'username' in data:
            print 'username'
            data['username'] = str(data.get('username')).lower()

        if 'email' in data:
            print 'email'
            data['email'] = str(data.get('email')).lower()

        serializer = serializers.CustomUserSerializer(data=data, many=False)

        if serializer.is_valid():
            custom_user = models.CustomUser(
                username=str(data.get('username')).lower(),
                email=str(data.get('email')).lower(),
                first_name=str(data.get('first_name')).capitalize(),
                last_name=str(data.get('last_name')).capitalize(),
                is_superuser=data.get('is_superuser'),
                is_principal=data.get('is_principal'),
                role=role,
                is_active=data.get('is_active'),
                method_id=data.get('method')
            )

            password = data.get('password')
            print '[[[PASWORD]]]'
            print password
            if password is None:
                print '[[[PASWORD ENTER]]]'
                password = data.get('username')
            custom_user.set_password(password)
            custom_user.save()

            print custom_user
            print '-----------'
            print 'ID USER: ' + str(custom_user.id)
            print 'EMAIL: ' + str(custom_user.email)
            print custom_user
            print custom_user.is_superuser
            print '-----------'

            user_profile_serializer = UserProfileSerializer
            new_data_profile = {"user_id": custom_user.id}

            user_profile = user_profile_serializer(data=new_data_profile, many=False)
            if user_profile.is_valid():
                user_profile.save()
                print 'SEND_EMAIL'
                print user_profile['created_at'].value
                hostname_origin = request.META.get('HTTP_ORIGIN')
                data = {
                    'fullname': str(custom_user.first_name) + ' ' + str(custom_user.last_name),
                    'username': str(custom_user.username),
                    'email': str(custom_user.email),
                    'is_superuser': custom_user.is_superuser,
                    'hostname': hostname_origin,
                    'is_active': custom_user.is_active,
                    'created_at': user_profile['created_at'].value
                }
                print data
                local_send_email(REGISTER, custom_user.email, data)
            else:
                custom_user.delete()
                return Response(user_profile.errors, status=status.HTTP_400_BAD_REQUEST)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAdminLocal]
    # permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = UserProfile.objects
        auth = self.request.query_params.get('auth', None)

        method = self.request.query_params.get('methodId', None)
        is_superuser = self.request.query_params.get('isSuperUser', None)
        exclude_owner = self.request.query_params.get('excludeOwner', None)

        query = Q()
        anyQuery = False
        if method is not None and method is not '':
            anyQuery = True
            try:
                query = query & Q(user__method__id=int(method))
            except:
                pass

        if is_superuser is not None and is_superuser.capitalize() in ['True', 'False']:
            anyQuery = True
            query = query & Q(user__is_superuser=is_superuser.capitalize())

        if exclude_owner is not None and exclude_owner.capitalize() in ['True']:
            if self.request.user.id:
                anyQuery = True
                ownerId = self.request.user.id
                query = query & ~Q(user__id=int(ownerId))

        if auth is not None:
            if self.request.user.id:
                ownerId = self.request.user.id
                query = query & Q(user__id=int(ownerId)) & Q(user__is_active=True)
                queryset = queryset.filter(query)
            else:
                print 'NO USER LOG'
                return []

        else:

            if anyQuery:
                queryset = queryset.filter(query).order_by('-updated_at')
            else:
                queryset = queryset.all().order_by('-updated_at')

        # print ownerId, self.request.user
        # print '------'
        return queryset



