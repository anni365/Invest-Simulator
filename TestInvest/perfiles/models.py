from __future__ import unicode_literals

from django.db import models

from django.contrib.auth.models import User, AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import MinValueValidator

from django.utils import timezone
from datetime import datetime


class CustomUser(AbstractUser):
    avatar = models.ImageField(upload_to='perfiles/',
                               default='perfiles/default.jpg')
    virtual_money = models.FloatField(
        validators=[MinValueValidator(0.0)], blank=None, default=1000
        )

    def __str__(self):
        return self.email

    def calculate_capital(assets, my_assets, virtual_money):
        cap = 0
        for name, dates in assets:
            date = list(dates.values())
            for asset in my_assets:
                if (asset.name == name[1] and date[1] is not None):
                    cap += asset.total_amount * date[1]
        cap += virtual_money
        return cap

    def update_money_user(request, total_amount, data, virtual_money):
        if request.get_full_path() == '/buy/':
            price = data[0]
            virtual_money -= total_amount * price
        else:
            price = data[1]
            virtual_money += total_amount * price
        request.user.virtual_money = virtual_money
        request.user.save()


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
    old_unit_value = models.FloatField(
        validators=[MinValueValidator(0.0)], blank=None
        )

    def addAsset(request, name, total_amount, type_asset, old_unit_value):
        asset = UserAsset.objects.create(
                  user_id=request.user.id, name=name, total_amount=total_amount,
                  type_asset=type_asset, old_unit_value=old_unit_value)
        asset.save()
        return asset

    def update_asset(asset, total_amount, data):
        asset.total_amount += total_amount
        asset.old_unit_value = data[0]
        asset.save()


class Transaction(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    user_asset = models.ForeignKey(UserAsset, on_delete=models.CASCADE)
    type_transaction = models.CharField(max_length=30)
    value_buy = models.FloatField(
        validators=[MinValueValidator(0.0)], blank=None
        )
    value_sell = models.FloatField(
        validators=[MinValueValidator(0.0)], blank=None
        )
    amount = models.PositiveIntegerField(blank=None)
    date = models.DateTimeField(max_length=50)

    def addTransaction(request, value_buy, value_sell, total_amount,
                       user_asset_id):
        if request.get_full_path() == '/buy/':
            type_t = str("compra")
        else:
            type_t = str("venta")
        transaction = Transaction.objects.create(user_id=request.user.id,
                                                 user_asset_id=user_asset_id,
                                                 value_buy=value_buy,
                                                 value_sell=value_sell,
                                                 amount=total_amount,
                                                 date=datetime.now(),
                                                 type_transaction=type_t)
        transaction.save()
        return transaction


class Alarm(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    name_asset = models.CharField(max_length=30)
    type_alarm = models.CharField(max_length=30)
    type_quote = models.CharField(max_length=30)
    type_umbral = models.CharField(max_length=30)
    previous_quote = models.FloatField(
        validators=[MinValueValidator(0.0)], blank=None)
    umbral = models.FloatField(
        validators=[MinValueValidator(0.0)], blank=None)
    email_send = models.BooleanField(default=False)

    def addAlarm(request, type_alarm, type_quote, type_umbral,
                            umbral, previous_quote, name_asset):
        alarm = Alarm.objects.create(
                    user_id=request.user.id, name_asset=name_asset,
                    type_alarm=type_alarm, type_quote=type_quote,
                    type_umbral=type_umbral, umbral=umbral,
                    previous_quote=previous_quote)
        alarm.save()
        return alarm
