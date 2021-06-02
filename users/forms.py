from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile


class UserRegisterForm(UserCreationForm):
    first_name = forms.CharField(label="First Name")
    last_name = forms.CharField(label="Last Name")
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ["first_name","last_name","username", "email", "password1", "password2"]


class UserUpdateForm(forms.ModelForm):
    first_name = forms.CharField(label="First Name")
    last_name = forms.CharField(label="Last Name")
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ["first_name","last_name","username", "email"]


class ProfileUpdateForm(forms.ModelForm):
    description = forms.CharField(required=False)
    class Meta:
        model = Profile
        fields = ["description", "image"]
