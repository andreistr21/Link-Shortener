from django import forms
from django.contrib.auth import authenticate, get_user_model
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


class SignInForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={"autofocus": True, "max_length": 150}))
    password = forms.CharField(widget=forms.PasswordInput)

    def __init__(self, request=None, *args, **kwargs):
        self.user_cache = None
        self.request = request
        self.email_field = get_user_model()._meta.get_field(get_user_model().USERNAME_FIELD)
        super(SignInForm, self).__init__(*args, **kwargs)

    def clean(self):
        super().clean()
        email = self.cleaned_data.get("email")
        password = self.cleaned_data.get("password")

        if email and password:
            self.user_cache = authenticate(self.request, email=email, password=password)
            if self.user_cache is None:
                self.invalid_login_error()
            else:
                self.confirm_login_allowed()

        return self.cleaned_data

    def confirm_login_allowed(self):
        if not self.user_cache.is_email_confirmed:
            self.add_error(
                None,
                "Email for this account not confirmed. Confirmation link was sent to your email during registration.",
            )
        if not self.user_cache.is_active:
            self.add_error(
                None,
                "This account is inactive",
            )

    def invalid_login_error(self):
        self.add_error(
            None,
            f"Please enter a correct {self.email_field} and password. Note that both fields may be case-sensitive.",
        )
