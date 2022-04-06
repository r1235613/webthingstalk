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


class Device(models.Model):
    type = models.TextField(blank=False)
    url = models.TextField(blank=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    token = models.TextField(blank=False)

    name = models.TextField(blank=True, unique=True)
    model = models.TextField(blank=True)
    claim = models.TextField(blank=True)

    href = models.TextField(null=True)

    creat_time = models.DateTimeField(auto_now_add=True)
    start_time = models.DateTimeField(null=True)

    def to_dict(self):
        return {'type': self.type, 'url': self.url, 'token': self.token, 'name': self.name, 'model': self.model, 'claim': self.claim, 'checked': self.checked, 'connected': self.connected}


class DeviceProperty(models.Model):
    name = models.TextField(blank=False)
    property = models.TextField(blank=False)
    idf = models.TextField(blank=False)
    odf = models.TextField(null=True)
    device_name = models.ForeignKey(
        Device, on_delete=models.CASCADE, related_name='property')
