from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.forms import ModelForm

from .models import *

class UserLogoForm(ModelForm):
    class Meta:
        model = Profile
        fields = ['logo_image']

class UserBioForm(ModelForm):
    class Meta:
        model = Profile
        fields = ['bio']

class RegisterUserForm(UserCreationForm):  # класс формы регистрации
    username = forms.CharField(label="Login",widget=forms.TextInput(attrs={'placeholder': 'Enter your login'}))
    email = forms.EmailField(label="Email",widget=forms.TextInput(attrs={'placeholder': 'Enter your email'}))
    first_name = forms.CharField(label="Name",widget=forms.TextInput(attrs={'placeholder': 'Enter your name'}))
    last_name = forms.CharField(label="Surname",widget=forms.TextInput(attrs={'placeholder': 'Enter your surname'}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Enter your password'}),label="Password")
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Repeat your password'}),label="Repeat password")
    class Meta:
        model = get_user_model()  # привязываем форму к модели
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')  # указываем нужные нам поля


class LoginPage(AuthenticationForm):
    username = forms.CharField(label='Login', widget=forms.TextInput(attrs={'placeholder':'Enter your login'}))
    password = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'placeholder':'Enter your password'}))
