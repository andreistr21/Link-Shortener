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
