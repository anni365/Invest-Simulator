# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render, redirect, render_to_response
from django.contrib.auth import login, authenticate, update_session_auth_hash
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import CreateView, TemplateView
from django.contrib.auth.forms import PasswordChangeForm

from .forms import SignUpForm, BuyForm
from django.contrib import messages
from .models import CustomUser, UserAsset
import json


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
    cap = 0
    for name, dates in assets:
        date = list(dates.values())
        for asset in my_assets:
            if (asset.name == name[1] and date[1] is not None):
                cap += asset.total_amount * date[1]
            cap += virtual_money
    return cap

def show_assets(request):
    user = request.user
    virtual_money = request.user.virtual_money
    my_assets = UserAsset.objects.filter(user=request.user.id)
    assets = open_jsons()
    cap = calculate_capital(assets, my_assets, virtual_money)
    if request.get_full_path() == '/buy/':
        form = BuyForm()
        return render(request, 'perfiles/buy.html', {
          'assets': assets, 'virtual_money': virtual_money, 'form': form})
    if request.get_full_path() == '/price/':
        return render_to_response('perfiles/price.html', {'assets': assets})
    if request.get_full_path() == '/wallet/':
        return render_to_response('perfiles/wallet.html', {
          'assets': assets, 'user': user, 'my_assets': my_assets,
          'capital': cap})
