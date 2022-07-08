from django.db import models
from django.contrib.auth.models import User


class Tier(models.Model):
    original_file_link = models.BooleanField()
    expiring_links = models.BooleanField()


class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    tier = models.ForeignKey(Tier, on_delete=models.PROTECT)


class Image(models.Model):
    image = models.ImageField(upload_to='images/')
    account = models.ForeignKey(Account, on_delete=models.CASCADE)


class Thumbnail(models.Model):
    height = models.IntegerField()
    tier = models.ForeignKey(Tier, on_delete=models.CASCADE)