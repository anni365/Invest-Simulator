from django import forms
from django.contrib.auth.forms import (
  UserCreationForm, AuthenticationForm, PasswordChangeForm)
from django.contrib.auth.models import User
from .models import CustomUser, UserAsset
from django.contrib.auth.forms import UserChangeForm
from django.core.files.images import get_image_dimensions
from django.forms import ModelForm


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(label="Nombre", max_length=140, required=True)
    last_name = forms.CharField(label="Apellido", max_length=140,
                                required=True)
    email = forms.EmailField(required=True)
    email2 = forms.EmailField(label='Email (confirmacion)', required=True)

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
    last_name = forms.CharField(label="Apellido", max_length=140,required=True)
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
    name = forms.CharField(disabled=True, required=False, label="Nombre del Activo")
    total_amount = forms.IntegerField(label="Cantidad Activo", required=False)

    class Meta:
        model = UserAsset
        fields = (
            'name',
            'total_amount',
        )
