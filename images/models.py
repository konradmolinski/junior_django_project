from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token


def default_thumbnail_sizes_list():
    return [200]


class Tier(models.Model):
    thumbnail_sizes = models.JSONField(default=default_thumbnail_sizes_list)
    original_image_link_bool = models.BooleanField()
    expiring_link_bool = models.BooleanField()


class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    tier = models.ForeignKey(Tier, default=1, on_delete=models.PROTECT)


class Image(models.Model):
    image = models.ImageField(upload_to='images/')
    account = models.ForeignKey(Account, on_delete=models.CASCADE)


class Thumbnail(models.Model):
    original_image = models.ForeignKey(Image, on_delete=models.CASCADE)
    thumbnail = models.ImageField(upload_to='thumbnails/', null=True)


class BinaryImage(models.Model):
    original_image = models.ForeignKey(Image, on_delete=models.CASCADE)
    binary_image = models.ImageField(upload_to='binary_images/')
    expiration_date = models.DateTimeField()


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