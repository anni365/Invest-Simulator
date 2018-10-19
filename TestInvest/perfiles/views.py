# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render, redirect, render_to_response, get_object_or_404
from django.contrib.auth import login, authenticate, update_session_auth_hash
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import CreateView, TemplateView, UpdateView
from django.contrib.auth.forms import PasswordChangeForm

from .forms import SignUpForm, UpdateProfileForm
from django.contrib import messages
from .models import CustomUser, Asset
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
    my_assets = Asset.objects.filter(user = request.user.id)
    return render_to_response('perfiles/wallet.html', { 'my_assets':  my_assets,
                              'user': user})


def show_assets(request):
    with open('perfiles/assets.json') as assets_json:
        assets = json.load(assets_json)
    assets = assets.get("assets")
    return render_to_response('perfiles/price.html', {'assets': assets})

class ProfileView(TemplateView):
    template_name = 'perfiles/profile.html'

#Editar perfil del usuario
class UpdateProfileView(UpdateView):
    model = CustomUser
    template_name = 'perfiles/update_profile.html'
    form_class = UpdateProfileForm

    def get_object(self):
        return get_object_or_404(CustomUser, pk=self.request.user.id)
