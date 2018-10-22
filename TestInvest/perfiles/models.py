from __future__ import unicode_literals

from django.db import models

from django.contrib.auth.models import User, AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver


class CustomUser(AbstractUser):
    avatar = models.ImageField(upload_to='perfiles/', default='perfiles/default.jpg')
    virtual_money = models.PositiveIntegerField(blank=None,default=1000)

    def __str__(self):
        return self.email

@receiver(post_save, sender=User)
def crear_usuario_perfil(sender, instance, created, **kwargs):
    if created:
        Perfil.objects.create(usuario=instance)


@receiver(post_save, sender=User)
def guardar_usuario_perfil(sender, instance, **kwargs):
    instance.perfil.save()

class UserAsset(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    type_asset = models.CharField(max_length=30)
    total_amount = models.PositiveIntegerField(blank=None)
    old_unit_value = models.PositiveIntegerField(blank=None)


class Transaction(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    user_asset = models.ForeignKey(UserAsset, on_delete=models.CASCADE)
    type_transaction = models.CharField(max_length=30)
    value_buy = models.PositiveIntegerField(blank=None)
    value_sell = models.PositiveIntegerField(blank=None)
    amount = models.PositiveIntegerField(blank=None)
    date = models.DateTimeField('date published')

