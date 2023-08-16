# from django.contrib.auth.models import AbstractUser
# from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import models


# class User(AbstractUser):
class User(AbstractUser):
    email = models.EmailField()


# class FriendShip(models.Model):
