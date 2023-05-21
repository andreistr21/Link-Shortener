from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Profile


class SignUpForm(UserCreationForm):
    class Meta:
        model = Profile
        fields = (
            "email",
            "password1",
            "password2",
        )


class SignInForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = (
            "email",
            "password",
        )
