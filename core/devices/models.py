from xtalk_template.models import AbstractUser


class User(AbstractUser):
    @property
    def is_staff(self):
        return self.staff
