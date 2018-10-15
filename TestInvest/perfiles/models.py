from __future__ import unicode_literals

from django.db import models

from django.contrib.auth.models import User, AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver


class CustomUser(AbstractUser):
    avatar = models.ImageField(upload_to='perfiles/', default='perfiles/default.jpg')

    def __str__(self):
        return self.email

class Wallet(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    virtual_money = models.PositiveIntegerField(blank=None)
    virtual_money = 1000

    # Python 3
    def __str__(self):
        return self.usuario.username

@receiver(post_save, sender=User)
def crear_usuario_perfil(sender, instance, created, **kwargs):
    if created:
        Perfil.objects.create(usuario=instance)


@receiver(post_save, sender=User)
def guardar_usuario_perfil(sender, instance, **kwargs):
    instance.perfil.save()

class Asset(models.Model):
    user = models.ForeignKey(CustomUser, default='', on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    cant = models.PositiveIntegerField(blank=None)
    old_unit_value = models.PositiveIntegerField(blank=None)
    date = models.DateTimeField('date published')

