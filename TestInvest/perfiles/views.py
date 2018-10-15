# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render, redirect, render_to_response
from django.contrib.auth import login, authenticate, update_session_auth_hash
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import CreateView, TemplateView
from django.contrib.auth.forms import PasswordChangeForm

from .forms import SignUpForm
from django.contrib import messages
from .models import CustomUser
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
        return redirect('/')


class BienvenidaView(TemplateView):
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


class WalletView(TemplateView):
    template_name = 'perfiles/wallet.html'


def show_wallet(request):
    portfolio_quote = "$1,520,000"
    liquid_money = "$100,000"
    with open('perfiles/wallet.json') as wallet_json:
        wallet = json.load(wallet_json)
    if wallet != []:
        wallet = wallet.get("wallet")
    return render_to_response('perfiles/wallet.html', {'wallet':  wallet,
                              'portfolio_quote': portfolio_quote,
                               'liquid_money': liquid_money})


def show_assets(request):
    with open('perfiles/assets.json') as assets_json:
        assets = json.load(assets_json)
    assets = assets.get("assets")
    return render_to_response('perfiles/price.html', {'assets': assets})
