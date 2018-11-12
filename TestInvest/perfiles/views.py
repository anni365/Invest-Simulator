# -- coding: utf-8 --
from __future__ import unicode_literals
from django.shortcuts import (render, render_to_response, get_object_or_404,
                              redirect)
from django.contrib.auth import login, authenticate, update_session_auth_hash
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import CreateView, TemplateView, UpdateView
from django.contrib.auth.forms import PasswordChangeForm
from .forms import (SignUpForm, BuyForm, SellForm, UpdateProfileForm,
                    AssetForm, AlarmForm, Visibility, LowAlarmForm)
from django.contrib import messages
from .models import CustomUser, UserAsset, Transaction, Alarm
import json
import threading
import time
from django.template import RequestContext
from django.utils import timezone
from datetime import datetime
from django.core.mail import EmailMessage, send_mail


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
    cap = CustomUser.calculate_capital(assets, my_assets, virtual_money)
    form = Visibility(request.POST)
    if form.is_valid():
        name = form.cleaned_data.get("name")
        visibility = form.cleaned_data.get("visibility")
        for asset in my_assets:
            if (name == asset.name):
                asset.visibility = visibility
                asset.save()
                my_assets = UserAsset.objects.filter(user=request.user.id)
                my_assets = my_assets.filter(total_amount__gt=0)
                return render(request, 'perfiles/wallet.html',
                                       {'assets': assets, 'user': user,
                                        'my_assets': my_assets,
                                        'capital': cap, 'form': form})
    return render(request, 'perfiles/wallet.html',
                           {'assets': assets, 'user': user,
                            'my_assets': my_assets, 'capital': cap,
                            'form': form})


def sell_assets(request):
    user = CustomUser
    virtual_money = request.user.virtual_money
    assets = open_jsons()
    form = SellForm(request.POST)
    if form.is_valid():
        name = form.cleaned_data.get("name")
        total_amount = form.cleaned_data.get("total_amount")
        my_assets = UserAsset.objects.filter(user=request.user.id, name=name)
        for names, dates in assets:
            date = list(dates.values())
            if my_assets.exists():
                for asset in my_assets:
                    if ((names[1] == asset.name) & (asset.total_amount > 0)):
                        asset.total_amount = asset.total_amount - total_amount
                        asset.save()
                        transaction = Transaction.addTransaction(
                                      request, date[0], date[1],
                                      total_amount, asset.id)
                        virtual_money = CustomUser.update_money_user(
                          request, total_amount, date, virtual_money)
                        return redirect('http://localhost:8000/wallet')
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
    mj = False
    cap = CustomUser.calculate_capital(assets, my_assets, virtual_money)
    if request.get_full_path() == '/buy/':
        if request.method == 'POST':
            form = BuyForm(request.POST)
            virtual_money, assets, mj = buy_assets(
              request, form, assets, virtual_money, mj)
        else:
            form = BuyForm()
        return render(request, 'perfiles/buy.html', {
          'assets': assets_a, 'virtual_money': virtual_money, 'form': form,
          'mj': mj})
    if request.get_full_path() == '/price/':
        return render_to_response('perfiles/price.html', {'assets': assets_a,
                                  'user': user})
    if request.get_full_path() == '/wallet/':
        return render_to_response('perfiles/wallet.html', {
          'assets': assets, 'user': user, 'my_assets': my_assets,
          'capital': cap})


def buy_assets(request, form, assets, capital, mj):
    virtual_money = request.user.virtual_money
    if form.is_valid():
        name = form.cleaned_data.get("name")
        total_amount = form.cleaned_data.get("total_amount")
        visibility = form.cleaned_data.get("visibility")
        assets_user = UserAsset.objects.filter(user=request.user.id, name=name)
        for nametype, prices in assets:
            data = list(prices.values())
            if nametype[1] == name and (data[0] is None or data[1] is None):
                messages.add_message(
                  request, messages.INFO, 'El Activo seleccionado ya no se'
                  'encuentra  disponible, no se pudo concretar la compra. Para'
                  ' ver la actual lista de activos recargue la pagina')
                break
            addOperation(request, assets_user, nametype, name,
                         total_amount, data, virtual_money, visibility)
            virtual_money = request.user.virtual_money
            mj = True
        return virtual_money, assets, mj


def addOperation(request, assets_user, nametype, name_form,
                 total_amount, data, virtual_money, visibility):
    if assets_user.exists():
        for asset in assets_user:
            if (nametype[1] == asset.name):
                UserAsset.update_asset(asset, total_amount, data, visibility)
                transaction = Transaction.addTransaction(
                  request, data[0], data[1], total_amount, asset.id)
                CustomUser.update_money_user(
                  request, total_amount, data, virtual_money)
    elif (nametype[1] == name_form):
        asset_user = UserAsset.addAsset(request, name_form, total_amount,
                                        nametype[0], data[0], visibility)
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


def cons_ranking():
    assets = open_jsons()
    dict_cap = {}
    users = CustomUser.objects.all()
    i = 1
    ranking = []
    for user in users:
        assets_users = UserAsset.objects.filter(user=user.id)
        capital = CustomUser.calculate_capital(assets, assets_users,
                                               user.virtual_money)
        dict_cap.update({user.username: capital})
    dict_items = dict_cap.items()
    list_cap = sorted(dict_items, key=lambda x: x[1], reverse=True)
    total_user = CustomUser.objects.count()
    for i in range(total_user):
        ranking.append((i+1,) + list_cap[i])
    return ranking


def ranking(request):
    list_cap = cons_ranking()
    users = CustomUser.objects.all()
    return render_to_response('perfiles/see_ranking.html',
                              {'lista_capital': list_cap,
                               'user': request.user})


def open_json_history(name_asset):
    name_as = 'perfiles/asset/'+name_asset+'_history.json'
    with open(name_as) as assets_json:
        assets_name = json.load(assets_json)
    assets_name = assets_name.get("prices")
    return assets_name


def get_asset_history(asset_history, since_date, until_date):
    history = []
    history_from_to = []
    i = 0
    for key, value in asset_history:
        day = asset_history[i][key]
        sell = asset_history[i][value][0]
        buy = asset_history[i][value][1]
        history.append([day, float(sell), float(buy)])
        i += 1
    for element in history:
        date = datetime.strptime(element[0], "%Y-%m-%d").date()
        since = datetime.strptime(since_date, "%Y-%m-%d").date()
        until = datetime.strptime(until_date, "%Y-%m-%d").date()
        if date >= since and date <= until:
            history_from_to.append([element[0], element[1], element[2]])
    if not history_from_to:
        for element in history:
            history_from_to.append([element[0], element[1], element[2]])
    return history_from_to


def assets_history(request):
    assets = open_jsons()
    assets_a = quit_null_assets(assets)
    form = AssetForm()
    if request.method == 'POST':
        form = AssetForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data.get("name")
            since_date = form.cleaned_data.get("since")
            until_date = form.cleaned_data.get("until")
            asset_history = open_json_history(name)
            is_history = True
            history_from_to = []
            history_from_to = get_asset_history(
              asset_history, since_date, until_date)
            grap_history = [["Fecha", "Venta", "Compra"]]
            grap_history += history_from_to
            return render(request, 'perfiles/assets_history.html', {
              'history': history_from_to, 'is_history': is_history,
              'name_asset': name, 'grap': json.dumps(grap_history)})
    return render(request, 'perfiles/assets_history.html', {'assets': assets_a,
                                                            'form': form})


def send_email(list_alarms):
    email_from = 'investsimulatorarg@gmail.com'
    for alarm in list_alarms:
        user = CustomUser.objects.get(pk=alarm[0])
        subject = ("[Invest Simulator] El activo " + str(alarm[1]) +
                   " ha alcanzado el valor esperado")
        body = ("El activo " + str(alarm[1]) +
                " ha alcanzado el valor esperado de " + str(alarm[2]) + ".\n"
                + str(alarm[1]) + "\nValor de cotización previo: " +
                str(alarm[4]) + "\n" + "Valor actual: " + str(alarm[3]) +
                "\nFecha: " + str(datetime.now()))
        send_mail(subject, body, email_from, [user.email], fail_silently=False)


def get_data_of_alarm():
    list_alarms = []
    assets = open_jsons()
    assets = quit_null_assets(assets)
    alarms_buy = Alarm.objects.filter(type_quote="buy", type_alarm="high")
    alarms_sell = Alarm.objects.filter(type_quote="sell", type_alarm="high")
    update_alarm_notif(alarms_buy, list_alarms, assets, 1)
    update_alarm_notif(alarms_sell, list_alarms, assets, 0)
    send_email(list_alarms)


def update_alarm_notif(alarms, list_alarms, assets_json, price):
    for alarm in alarms:
        for nametype, prices in assets_json:
            data = list(prices.values())
            if nametype[1] == alarm.name_asset:
                check_alarms_json(list_alarms, alarm, data, price, nametype)


def check_alarms_json(list_alarms, alarm, data, price, nametype):
    if alarm.umbral >= data[price] and alarm.type_umbral == "less":
        if not alarm.email_send:
            update_list_alarm(list_alarms, alarm, nametype, data, price)
    elif alarm.type_umbral == "less" and alarm.email_send:
        update_list_alarm(list_alarms, alarm, nametype, data, price)
    if alarm.umbral <= data[price] and alarm.type_umbral == "top":
        if not alarm.email_send:
            update_list_alarm(list_alarms, alarm, nametype, data, price)
    elif alarm.type_umbral == "top" and alarm.email_send:
        update_list_alarm(list_alarms, alarm, nametype, data, price)


def update_list_alarm(list_alarms, alarm, nametype, data, price):
    if alarm.email_send:
        alarm.email_send = False
    else:
        list_alarms.append([alarm.user_id, nametype[1], alarm.umbral,
                            data[price], alarm.previous_quote])
        alarm.email_send = True
    alarm.save()


def list_alarms(request):
    alarms = Alarm.objects.filter(user_id=request.user.id, type_alarm="high")
    list_alarms = []
    for alarm in alarms:
        name_asset = alarm.name_asset
        type_umbral = alarm.type_umbral
        umbral = alarm.umbral
        id_alarm = alarm.id
        if type_umbral == "top":
            type_umbral = "Superior"
        elif type_umbral == "less":
            type_umbral = "Inferior"
        list_alarms.append((name_asset, type_umbral, umbral, id_alarm))
    return list_alarms


def low_alarms(request, id_alarm):
    alarms = Alarm.objects.filter(user_id=request.user.id, type_alarm="high")
    for alarm in alarms:
        if int(id_alarm) == alarm.id:
            alarm.type_alarm = "low"
            alarm.save()


def view_alarm(request):
    list_alarm = list_alarms(request)
    if request.method == 'POST':
        form_low = LowAlarmForm(request.POST)
        user = request.user.id
        if form_low.is_valid():
            id_low = form_low.cleaned_data.get("name_low")
            low_alarms(request, id_low)
            list_alarm = list_alarms(request)
        return render(request, 'perfiles/view_alarms.html', {
          'view_alarms': list_alarm, 'form_low': LowAlarmForm()})
    else:
        form_low = LowAlarmForm()
    return render(
      request, 'perfiles/view_alarms.html',
      {'view_alarms': list_alarm, 'form_low': form_low})


def config_alarm(request):
    get_data_of_alarm()
    assets = open_jsons()
    assets = quit_null_assets(assets)
    if request.method == 'POST':
        form = AlarmForm(request.POST)
        user = request.user.id
        if form.is_valid():
            type_alarm = form.cleaned_data.get("type_alarm")
            type_quote = form.cleaned_data.get("type_quote")
            type_umbral = form.cleaned_data.get("type_umbral")
            previous_quote = form.cleaned_data.get("previous_quote")
            umbral = form.cleaned_data.get("umbral")
            name_asset = form.cleaned_data.get("name_asset")
            alarm = Alarm.addAlarm(request, type_quote,
                                   type_umbral, umbral, previous_quote,
                                   name_asset)
            list_alarm = list_alarms(request)
        return render(request, 'perfiles/view_alarms.html', {
          'view_alarms': list_alarm, 'form_low': LowAlarmForm()})
    else:
        form = AlarmForm()
    return render(request, 'perfiles/alarm.html', {
      'assets': assets, 'form': form})


def consult_alarm_forever():
    while True:
        get_data_of_alarm()
        time.sleep(15)


def hilo():
    hilo = threading.Thread(target=consult_alarm_forever)
    hilo.setDaemon(True)
    hilo.start()


hilo()


def visibility_investments(request):
    ranking = cons_ranking()
    all_assets = open_jsons()
    assets_a = quit_null_assets(all_assets)
    investments_v = UserAsset.objects.filter(visibility=True)
    datas = []
    for invest in investments_v:
        assets = UserAsset.objects.filter(user_id=invest.user_id,
                                          name=invest.name)
        for asset in assets:
            ult_trans = Transaction.objects.filter(user_id=invest.user_id,
                                                   type_transaction='compra',
                                                   user_asset_id=asset.id)
            ult_trans = ult_trans.last()
            datas.append([invest.user_id, asset.name, ult_trans.date,
                          ult_trans.value_sell])
    return render_to_response('perfiles/visibility_investments.html',
                              {'user': request.user,
                               'investments_v': investments_v,
                               'ranking': ranking,
                               'datas': datas, 'assets': assets_a})
