# -- coding: utf-8 --
from __future__ import unicode_literals
from django.shortcuts import render, render_to_response, get_object_or_404
from django.contrib.auth import login, authenticate, update_session_auth_hash
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import CreateView, TemplateView, UpdateView
from django.contrib.auth.forms import PasswordChangeForm
from .forms import SignUpForm, BuyForm, SellForm, UpdateProfileForm, AssetForm
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


class ProfileView(TemplateView):
    template_name = 'perfiles/profile.html'


class UpdateProfileView(UpdateView):
    model = CustomUser
    template_name = 'perfiles/update_profile.html'
    form_class = UpdateProfileForm

    def get_object(self):
        return get_object_or_404(CustomUser, pk=self.request.user.id)


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


def show_my_assets(request):
    user = request.user
    virtual_money = request.user.virtual_money
    my_assets = UserAsset.objects.filter(user=request.user.id)
    my_assets = my_assets.filter(total_amount__gt=0)
    assets = open_jsons()
    form = SellForm(request.POST)
    cap = CustomUser.calculate_capital(assets, my_assets, virtual_money)
    if request.get_full_path() == '/price/':
        return render_to_response('perfiles/price.html', {'assets': assets})
    if request.get_full_path() == '/wallet/':
        return render_to_response('perfiles/wallet.html', {'assets': assets,
                                  'user': user, 'my_assets': my_assets,
                                                           'capital': cap})


def sell_assets(request):
    user = CustomUser
    virtual_money = request.user.virtual_money
    assets = open_jsons()
    form = SellForm(request.POST)
    if form.is_valid():
        name = form.cleaned_data.get("name")
        total_amount = form.cleaned_data.get("total_amount")
        my_assets = UserAsset.objects.filter(user=request.user.id, name=name)
        exist = my_assets.exists()
        for names, dates in assets:
            date = list(dates.values())
            if exist:
                for asset in my_assets:
                    if ((names[1] == asset.name) & (asset.total_amount > 0)):
                        asset.total_amount = asset.total_amount - total_amount
                        asset.save()
                        transaction = Transaction.addTransaction(
                                      request, date[0], date[1],
                                      total_amount, asset.id)
                        virtual_money = CustomUser.update_money_user(
                          request, total_amount, date, virtual_money)
    return render(request, 'perfiles/salle.html', {
                  'assets': assets, 'my_assets': my_assets,
                  'virtual_money': virtual_money, 'form': form})


def quit_null_assets(assets):
    assets_a = []
    for keys, values in assets:
        if values['sell'] is not None and values['buy'] is not None:
            assets_a.append(((keys[0],  keys[1]), {"sell": values['sell'],
                            "buy": values['buy']}))
    return assets_a


def show_assets(request):
    user = request.user
    virtual_money = request.user.virtual_money
    my_assets = UserAsset.objects.filter(user=request.user.id)
    assets = open_jsons()
    assets_a = quit_null_assets(assets)
    cap = CustomUser.calculate_capital(assets, my_assets, virtual_money)
    if request.get_full_path() == '/buy/':
        if request.method == 'POST':
            form = BuyForm(request.POST)
            virtual_money, assets = buy_assets(
              request, form, assets, virtual_money)
        else:
            form = BuyForm()
        return render(request, 'perfiles/buy.html', {
          'assets': assets_a, 'virtual_money': virtual_money, 'form': form})
    if request.get_full_path() == '/price/':
        return render_to_response('perfiles/price.html', {'assets': assets_a})
    if request.get_full_path() == '/wallet/':
        return render_to_response('perfiles/wallet.html', {
          'assets': assets, 'user': user, 'my_assets': my_assets,
          'capital': cap})


def buy_assets(request, form, assets, capital):
    virtual_money = request.user.virtual_money
    if form.is_valid():
        name = form.cleaned_data.get("name")
        total_amount = form.cleaned_data.get("total_amount")
        assets_user = UserAsset.objects.filter(user=request.user.id, name=name)
        exist_asset = assets_user.exists()
        for nametype, prices in assets:
            data = list(prices.values())
            if nametype[1] == name and (data[0] is None or data[1] is None):
                messages.add_message(
                  request, messages.INFO, 'El Activo seleccionado ya no se'
                  'encuentra  disponible, no se pudo concretar la compra. Para'
                  'ver la actual lista de activos recargue la pagina')
                break
            addOperation(request, exist_asset, assets_user, nametype, name,
                         total_amount, data, virtual_money)
            virtual_money = request.user.virtual_money
        return virtual_money, assets


def addOperation(request, exist_asset, assets_user, nametype, name_form,
                 total_amount, data, virtual_money):
    if exist_asset:
        for asset in assets_user:
            if (nametype[1] == asset.name):
                CustomUser.update_asset(asset, total_amount, data)
                transaction = Transaction.addTransaction(
                  request, data[0], data[1], total_amount, asset.id)
                CustomUser.update_money_user(
                  request, total_amount, data, virtual_money)
    elif (nametype[1] == name_form):
        asset_user = UserAsset.addAsset(request, name_form, total_amount,
                                        nametype[0], data[0])
        transaction = Transaction.addTransaction(
          request, data[0], data[1], total_amount, asset_user.id)
        CustomUser.update_money_user(
          request, total_amount, data, virtual_money)
    return virtual_money


def mytransactions(request):
    my_transactions = Transaction.objects.filter(user=request.user.id)
    my_transactions = my_transactions.order_by('-date')
    return render_to_response(
      'perfiles/transaction_history.html', {
        'my_transactions': my_transactions, 'user': request.user})


def open_json_history(name_asset):
    name_as = 'perfiles/asset/'+name_asset+'_history.json'
    with open(name_as) as assets_json:
        assets_name = json.load(assets_json)
    assets_name = assets_name.get("prices")
    return assets_name


def assets_history(request):
    assets = open_jsons()
    assets_a = quit_null_assets(assets)
    form = AssetForm()
    if request.method == 'POST':
        form = AssetForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data.get("name")
            asset_history = open_json_history(name)
            is_history = True
            history = []
            i = 0
            for key, value in asset_history:
                day = asset_history[i][key]
                sell = asset_history[i][value][0]
                buy = asset_history[i][value][1]
                history.append([day,float(sell),float(buy)])
                i += 1
            grap_history = [["Fecha", "Venta", "Compra"]]
            j = 0
            for key, value in asset_history:
                day = asset_history[j][key]
                sell = asset_history[j][value][0]
                buy = asset_history[j][value][1]
                grap_history.append([day,float(sell),float(buy)])
                j += 1
            return render(request, 'perfiles/assets_history.html',
                          {'history': history, 'is_history': is_history,
                           'name_asset': name,
                           'grap': json.dumps(grap_history)})
    return render(request, 'perfiles/assets_history.html', {'assets': assets_a,
                                                            'form': form})
