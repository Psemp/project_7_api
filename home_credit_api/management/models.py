from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    """
    Profile class for user/agent which can interact or not with the dashboard.
    Extends the User class to provide password security for the data and estimations.
    is_staff created to grand or refuse access to data and dashboard, boolean changeable by
    superuser un admin interface.
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_staff = models.BooleanField(verbose_name="is_staff", default=False)

    def __str__(self):
        return f'{self.user.username} Profile'
