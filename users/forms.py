from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django import forms
from .models import User


class EditProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'avatar')
        labels = {
            'username': 'Логин',
            'first_name': 'Отображаемое имя',
            'avatar': 'Аватарка',
        }


class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'avatar')
        labels = {
            'username': 'Логин',
            'first_name': 'Отображаемое имя',
            'avatar': 'Аватарка',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].label = 'Пароль'
        self.fields['password2'].label = 'Повторите пароль'


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Логин'
        self.fields['password'].label = 'Пароль'
