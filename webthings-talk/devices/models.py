from operator import mod
from statistics import mode
from django.db import models
from django.conf import settings
from django.forms import modelformset_factory

from xtalk_template.models import AbstractUser
from xtalk_template.models import AbstractRefreshToken
from xtalk_template.models import AbstractAccessToken


class User(AbstractUser):
    pass


class RefreshToken(AbstractRefreshToken):
    pass


class AccessToken(AbstractAccessToken):
    pass


class DeviceUrl(models.Model):
    url = models.TextField(blank=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    create_time = models.DateTimeField(auto_now_add=True)


class GatewayUrl(models.Model):
    url = models.TextField(blank=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    token = models.TextField(blank=False)
    create_time = models.DateTimeField(auto_now_add=True)


class Device(models.Model):
    device_model = models.TextField(blank=True)
    device_base = models.TextField(blank=False)
    device_url = models.TextField(blank=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    token = models.TextField(blank=False)

    device_name = models.TextField(blank=True)

    creat_time = models.DateTimeField(auto_now_add=True)
    start_time = models.DateTimeField(null=True)

    class Meta:
        unique_together = (('user', 'device_name'),)


class DeviceProperty(models.Model):
    name = models.TextField(blank=False)
    property = models.TextField(blank=False)
    idf = models.TextField(blank=False)
    odf = models.TextField(null=True)
    device_name = models.ForeignKey(
        Device, on_delete=models.CASCADE, related_name='property')
