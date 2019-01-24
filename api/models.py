# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.conf import settings
from django.utils import timezone
# Create your models here.


class Volcano(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    latitude = models.CharField(max_length=45, blank=True, null=True)
    longitude = models.CharField(max_length=45, blank=True, null=True)
    height = models.IntegerField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return self.name


class Method(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    principal = models.CharField(max_length=100, blank=True, null=True)
    # principal = models.ForeignKey(UserProfile, on_delete=models.PROTECT, blank=True, null=True)
    color = models.CharField(max_length=50, blank=True, null=True)
    icon = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return self.name


class Technique(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    method = models.ForeignKey(Method, related_name='methods', on_delete=models.PROTECT, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True,)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True,)

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    # first_name = models.CharField(max_length=100, blank=True, null=True)
    # last_name = models.CharField(max_length=100, blank=True, null=True)
    # method = models.ForeignKey(Method, related_name='method_user', on_delete=models.CASCADE, blank=True, null=True)
    # is_principal = models.BooleanField(default=False)
    description = models.CharField(max_length=255, blank=True, null=True)
    # role = models.CharField(max_length=100, blank=True, null=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __unicode__(self):
        return str(self.id)

    def __str__(self):
        return self.user.username


class Parameter(models.Model):
    label = models.CharField(max_length=100, blank=True, null=True)
    unit = models.CharField(max_length=20, blank=True, null=True)
    state = models.BooleanField(default=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='owner_params', on_delete=models.SET_NULL, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return self.label


class Template(models.Model):
    label = models.CharField(max_length=100, blank=True, null=True)
    # parameters = models.CharField(max_length=255, blank=True, null=True)
    parameters_order = models.CharField(max_length=255, blank=True, null=True)
    parameters = models.ManyToManyField(Parameter, blank=True, related_name='template_parameters')
    technique = models.ForeignKey(Technique, related_name='techniques', on_delete=models.PROTECT, blank=True, null=True)
    volcano = models.ForeignKey(Volcano, on_delete=models.CASCADE, blank=True, null=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)
    state = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return self.label


class RowDefinitive(models.Model):
    description = models.TextField(blank=True, null=True)
    date = models.DateTimeField(default=timezone.now, blank=True, null=True)
    volcano = models.ForeignKey(Volcano, on_delete=models.CASCADE, blank=True, null=True)
    template = models.ForeignKey(Template, related_name='records', on_delete=models.PROTECT, blank=True, null=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)
    state = models.BooleanField(default=True)
    is_single_insert = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __unicode__(self):
        return str(self.id)

    def __str__(self):
        return str(self.id)
        # return self.date.strftime("%d-%m-%Y %H:%M:%S") + ' : ' + self.volcano.name + '-' + self.template.label


class RowDefinitiveData(models.Model):
    value = models.FloatField(blank=True, null=True, default=0.0)
    parameter = models.ForeignKey(Parameter, on_delete=models.PROTECT, blank=True, null=True)
    row_definitive = models.ForeignKey(RowDefinitive, related_name='data', on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.parameter.label + ':' + str(self.value)
        # return self.id


