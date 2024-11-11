from django.db import models
from django.conf import settings
# import datetime
# # Create your models here.

class Profile(models.Model):
    username = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(unique=True)
    user=models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name}'