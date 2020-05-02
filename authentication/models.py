from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    firebase_uid = models.TextField(blank=False, null=False)
    phone_number = models.TextField(blank=False, null=False)