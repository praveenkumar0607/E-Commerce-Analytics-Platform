from django.db import models
from django.conf import settings
import pandas as pd
import uuid
from datetime import datetime
from django.apps import apps
from core.models import User



def user_directory_path(instance, filename):
    return f'user_{instance.user.id}/{filename}'

class UserDataFile(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='+')
    file = models.FileField(upload_to=user_directory_path)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.file.name} uploaded by {self.user.name}"


class UserTable(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='+')
    table_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Table {self.table_name} created by {self.user.name}"