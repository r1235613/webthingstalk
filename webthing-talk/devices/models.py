from django.db import models

from xtalk_template.models import AbstractUser
from xtalk_template.models import AbstractRefreshToken
from xtalk_template.models import AbstractAccessToken


class User(AbstractUser):
    pass


class RefreshToken(AbstractRefreshToken):
    pass


class AccessToken(AbstractAccessToken):
    pass
