# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
# from api.models import Method
# Create your models here.
from django.conf import settings


class CustomUser(AbstractUser):
    is_principal = models.BooleanField(default=False)
    role = models.CharField(max_length=100, blank=True, null=True)
    method = models.ForeignKey(settings.METHOD_MODEL, related_name='method_user', on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.email

