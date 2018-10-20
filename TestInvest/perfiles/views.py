# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render, redirect, render_to_response
from django.contrib.auth import login, authenticate, update_session_auth_hash
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import CreateView, TemplateView
from django.contrib.auth.forms import PasswordChangeForm

from .forms import SignUpForm
from django.contrib import messages
from .models import CustomUser, UserAsset, Transaction
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

def show_my_asset(request):
    user = request.user
    my_assets = UserAsset.objects.filter(user = request.user.id)
    return render_to_response('perfiles/wallet.html', { 'my_assets':  my_assets,
                              'user': user})


def show_assets(request):
    with open('perfiles/assets.json') as assets_json:
        assets = json.load(assets_json)
    assets = assets.get("assets")
    return render_to_response('perfiles/price.html', {'assets': assets})

def mytransactions(request):
    my_transactions = Transaction.objects.filter(user = request.user.id).order_by('date')
    return render_to_response('perfiles/transaction_history.html',
                              {'my_transactions': my_transactions,
                              'user': request.user})

