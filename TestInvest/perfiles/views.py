# -- coding: utf-8 --
from __future__ import unicode_literals
from django.shortcuts import render, redirect, render_to_response
from django.contrib.auth import login, authenticate, update_session_auth_hash
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import CreateView, TemplateView
from django.contrib.auth.forms import PasswordChangeForm

from .forms import SignUpForm, BuyForm, SellForm
from django.contrib import messages
from .models import CustomUser, UserAsset, Transaction
import json
from django.template import RequestContext
from django.utils import timezone
from datetime import datetime

class SignUpView(CreateView):
    model = CustomUser
    form_class = SignUpForm
    template_name = 'perfiles/signup.html'

    def form_valid(self, form):
        form.save()
        usuario = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password1')
        usuario = authenticate(username=usuario, password=password)
        return render(self.request, 'perfiles/signup.html', {'form': form})


class WelcomeView(TemplateView):
    template_name = 'perfiles/home.html'


def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'perfiles/change_password.html', {
        'form': form
    })


class SignInView(LoginView):
    template_name = 'perfiles/login.html'


class SignOutView(LogoutView):
    pass

def open_jsons():
    print("OPEN JSONS")
    with open('perfiles/asset/assets.json') as assets_json:
        assets_name = json.load(assets_json)
    assets_name = assets_name.get("availableAssets")
    assets_price = []
    assets = {}
    cap = 0
    if assets_name is not None:
        for asset in assets_name:
            name_as = 'perfiles/asset/'+str(asset.get("name"))+'.json'
            with open(name_as) as assets_price:
                price = json.load(assets_price)
                assets.update({(asset.get("type"), asset.get("name")): price})
    assets = assets.items()
    return assets


def calculate_capital(assets, my_assets, virtual_money):
    print("CALCULATE CAPITAL")
    cap = 0
    for name, dates in assets:
        date = list(dates.values())
        for asset in my_assets:
            if (asset.name == name[1] and date[1] is not None):
                cap += asset.total_amount * date[1]
    cap += virtual_money
    return cap

def show_my_assets(request):
    print("SHOW MY ASSETS")
    user = request.user
    virtual_money = request.user.virtual_money
    my_assets = UserAsset.objects.filter(user=request.user.id)
    assets = open_jsons()
    form = SellForm(request.POST)
    cap = calculate_capital(assets, my_assets, virtual_money)
    if request.get_full_path() == '/price/':
        return render_to_response('perfiles/price.html', { 'assets': assets })
    if request.get_full_path() == '/wallet/':
        return render_to_response('perfiles/wallet.html', { 'assets': assets,
                                  'user': user, 'my_assets': my_assets, 
                                  'capital': cap })

def sell_assets(request):
    user = CustomUser
    virtual_money = request.user.virtual_money
    assets = open_jsons()
    form = SellForm(request.POST)
    if form.is_valid():
        name = form.cleaned_data.get("name")
        total_amount = form.cleaned_data.get("total_amount")
        my_assets =  UserAsset.objects.filter(user=request.user.id, name=name)
        exist = my_assets.exists()
        for names, dates in assets:
            date = list(dates.values())
            if exist:
                for asset in my_assets:
                    if ((names[1] == asset.name) & (asset.total_amount > 0)):
                        asset.total_amount = asset.total_amount - total_amount
                        asset.save()
                        transaction = addTransaction(
                                      request, date[0], date[1], 
                                      total_amount, asset.id)
            else:
              print("No existe el asset")
    return render(request, 'perfiles/salle.html', { 
                  'assets': assets, 'my_assets': my_assets, 
                  'virtual_money': virtual_money, 'form':form})


def addTransaction(request, value_buy, value_sell, total_amount, 
                   user_asset_id):
    if request.get_full_path() == '/buy/':
        type_t = str("compra")
    else:
        type_t = str("venta")
    transaction = Transaction.objects.create(user_id= request.user.id,
        user_asset_id = user_asset_id,
        value_buy = value_buy, 
        value_sell = value_sell,
        amount = total_amount,
        date = datetime.now(tz=timezone.utc),
        type_transaction = type_t)
    transaction.save()
    return transaction

def show_assets(request):
    user = request.user
    virtual_money = request.user.virtual_money
    my_assets = UserAsset.objects.filter(user=request.user.id)
    with open('perfiles/asset/assets.json') as assets_json:
        assets_name = json.load(assets_json)
    assets_name = assets_name.get("availableAssets")
    assets_price = []
    assets = {}
    cap = 0
    if assets_name is not None:
        for asset in assets_name:
            name_as = 'perfiles/asset/'+str(asset.get("name"))+'.json'
            with open(name_as) as assets_price:
                pri = json.load(assets_price)
                assets.update({(asset.get("type"), asset.get("name")): pri})
    assets = assets.items()
    for name, dates in assets:
      date = list(dates.values())
      for asset in my_assets:
        if (asset.name == name[1] and date[1] != None ):
          cap += asset.total_amount * date[1]
    cap += virtual_money
    if request.get_full_path() == '/buy/':
      if request.method == 'POST':
        form = BuyForm(request.POST)
        if form.is_valid():
          name = request.POST.get("name", "0")
          total_amount = form.cleaned_data.get("total_amount")
          my_assets =  UserAsset.objects.filter(user=request.user.id, name=name)
          exist = my_assets.exists()
          for names, dates in assets:
            date = list(dates.values())
            if exist:
              for asset in my_assets:
                print()
                if names[1] == asset.name:
                  asset.total_amount = asset.total_amount + total_amount
                  asset.old_unit_value = date[0] 
                  asset.save()
                  transaction = Transaction.objects.create(
                    user_id= request.user.id,
                    user_asset_id=asset.id, 
                    value_buy=date[0], value_sell=date[1], 
                    amount=total_amount,
                    date=datetime.now(),
                    type_transaction="compra")
                  transaction.save()
            else:
              if names[1] == name:
                my_asset = UserAsset.objects.create(
                  user_id= request.user.id, name=name,
                  total_amount=total_amount, type_asset=names[0],
                  old_unit_value=date[0])
                my_asset.save()
                transaction = Transaction.objects.create(
                  user_id= request.user.id,
                  user_asset_id=my_asset.id, 
                  value_buy=date[0], value_sell=date[1], 
                  amount=total_amount,
                  date=datetime.now(),
                  type_transaction="compra")
                transaction.save()
      else:
        form = BuyForm()
      return render(request, 'perfiles/buy.html', { 'assets': assets, 'virtual_money': virtual_money, 'form': form})
    if request.get_full_path() == '/price/':
      return render_to_response('perfiles/price.html', { 'assets': assets })
    if request.get_full_path() == '/wallet/':
      return render_to_response('perfiles/wallet.html', { 'assets': assets,
                                'user': user, 'my_assets': my_assets, "capital": cap })

#def addTransaction(request, value_buy, value_sell, amount, user_asset_id):

