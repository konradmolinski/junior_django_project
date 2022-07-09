from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from rest_framework.authtoken.models import Token

class Tier(models.Model):
    original_file_link = models.BooleanField()
    expiring_links = models.BooleanField()


class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    tier = models.ForeignKey(Tier, null=True, on_delete=models.PROTECT)


class Image(models.Model):
    image = models.ImageField(upload_to='images/')
    account = models.ForeignKey(Account, on_delete=models.CASCADE)


class Thumbnail(models.Model):
    height = models.IntegerField()
    tier = models.ForeignKey(Tier, on_delete=models.CASCADE)


@receiver(post_save, sender=User)
def create_user_account(sender, instance, created, **kwargs):
    if created:
        Account.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_account(sender, instance, **kwargs):
    instance.account.save()


@receiver(post_save, sender=User)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)