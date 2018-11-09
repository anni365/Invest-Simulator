from django import forms
from django.contrib.auth.forms import (
  UserCreationForm, AuthenticationForm, PasswordChangeForm)
from django.contrib.auth.models import User
from .models import CustomUser, UserAsset, Alarm
from django.contrib.auth.forms import UserChangeForm
from django.core.files.images import get_image_dimensions
from django.forms import ModelForm


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(label="Nombre", max_length=140, required=True)
    last_name = forms.CharField(label="Apellido", max_length=140,
                                required=True)
    email = forms.EmailField(required=True, widget=forms.TextInput(attrs={
                            'placeholder': 'usuario@usuario.com'
                        })
                )
    email2 = forms.EmailField(label='Email (confirmacion)', required=True,
                              widget=forms.TextInput(
                                attrs={
                                    'placeholder': 'usuario@usuario.com'
                                })
                              )

    def clean_email2(self):
        email = self.cleaned_data.get("email")
        email2 = self.cleaned_data.get("email2")
        if email and email != email2:
            raise forms.ValidationError("Los 2 campos de emails no coinciden")
        return email2

    class Meta:
        model = CustomUser
        fields = (
            'username',
            'email',
            'email2',
            'first_name',
            'last_name',
            'password1',
            'password2',
            'avatar',
        )


class UpdateProfileForm(forms.ModelForm):
    first_name = forms.CharField(label="Nombre", max_length=140, required=True)
    last_name = forms.CharField(label="Apellido", max_length=140,
                                required=True)
    email = forms.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = (
            'first_name',
            'last_name',
            'email',
            'avatar',
        )


class BuyForm(ModelForm):
    name = forms.CharField(required=False, label="Nombre del Activo")
    total_amount = forms.IntegerField(label="Cantidad Activo", required=False)

    class Meta:
        model = UserAsset
        fields = (
            'name',
            'total_amount',
        )


class SellForm(forms.Form):
    name = forms.CharField(required=False, label="Nombre del Activo")
    total_amount = forms.IntegerField(label="Cantidad Activo", required=False)
    price_sell = forms.CharField(label="Precio de Venta", required=False)
    virtual_money = forms.CharField(label="Dinero Liquido", required=False)


class DateInput(forms.DateTimeInput):
    input_type = 'date'


class TimeInput(forms.TimeInput):
    input_type = 'time'


class AssetForm(forms.Form):
    name = forms.CharField(required=False)
    since = forms.CharField(widget=DateInput())
    time_since = forms.CharField(widget=TimeInput())
    until = forms.CharField(widget=DateInput())
    time_until = forms.CharField(widget=TimeInput())

    def __init__(self, *args, **kwargs):
        super(AssetForm, self).__init__(*args, **kwargs)
        self.fields['name'].label = 'Nombre'
        self.fields['since'].label = 'Desde'
        self.fields['time_since'].label = 'Hora'
        self.fields['until'].label = 'Hasta'
        self.fields['time_until'].label = 'Hora'


class AlarmForm(ModelForm):
    type_alarm = forms.ChoiceField(required=True, choices=(
      ('high', 'Alta'), ('low', 'Baja')))
    type_quote = forms.ChoiceField(required=True, choices=(
      ('buy', 'Compra'), ('sell', 'Venta')))
    type_umbral = forms.ChoiceField(required=True, choices=(
      ('less', 'Inferior'), ('top', 'Superior')))

    def __init__(self, *args, **kwargs):
        super(AlarmForm, self).__init__(*args, **kwargs)
        self.fields['type_alarm'].label = 'Tipo de Alarma'
        self.fields['type_quote'].label = 'Tipo de Cotización'
        self.fields['type_umbral'].label = 'Tipo de Umbral'
        self.fields['previous_quote'].label = 'Valor actual'
        self.fields['previous_quote'].widget = forms.TextInput(attrs={
          'placeholder': 'Elija un Activo Disponible'})
        self.fields['umbral'].label = 'Precio'
        self.fields['name_asset'].label = 'Nombre del Activo'
        self.fields['name_asset'].widget = forms.TextInput(attrs={
          'placeholder': 'Elija un Activo Disponible'})

    class Meta:
        model = Alarm
        fields = (
            'type_alarm',
            'type_quote',
            'type_umbral',
            'previous_quote',
            'umbral',
            'name_asset',
        )


class LowAlarmForm(forms.Form):
    name_low = forms.CharField(label="¿Desea dar de baja la alarma sobre el activo")
    umbral_low = forms.CharField(label="con umbral:")
    price_low = forms.FloatField(label="al precio:")

