from django import forms
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm


class SignupForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        # fields = ('username')


class LoginForm(forms.Form):
    username = forms.CharField(max_length=100, label='Nom d’utilisateur')
    pass_word = forms.CharField(max_length=100, widget=forms.PasswordInput, label='Mot de passe')


class FollowUser(forms.Form):
    username = forms.CharField(max_length=100)


class TicketForm(forms.Form):
    title = forms.CharField(max_length=128)
    description = forms.CharField(max_length=2048)
    image = forms.ImageField()


class ReviewForm(forms.Form):
    # Ticket part
    title = forms.CharField(max_length=128)
    description = forms.CharField(max_length=2048)
    image = forms.ImageField()

    # Review part
    headline = forms.CharField(max_length=128)
    body = forms.CharField(max_length=8192)
    rating = forms.CharField(max_length=10)


class ReviewModifyForm(forms.Form):
    # Review part
    headline = forms.CharField(max_length=128)
    body = forms.CharField(max_length=8192)
    rating = forms.CharField(max_length=10)
