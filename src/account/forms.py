from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import SetPasswordForm, UserCreationForm

from account.models import Profile


class SignUpForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["password1"].widget.attrs.update({"placeholder": "Password"})
        self.fields["password2"].widget.attrs.update({"placeholder": "Repeat password"})

    class Meta:
        model = Profile
        fields = (
            "email",
            "password1",
            "password2",
        )
        widgets = {
            "email": forms.EmailInput(attrs={"placeholder": "Your email"}),
        }


class SignInForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={"autofocus": True, "max_length": 150, "placeholder": "your email"}
        )
    )
    password = forms.CharField(widget=forms.PasswordInput(attrs={"placeholder": "password"}))

    def __init__(self, request=None, *args, **kwargs):
        self.user_cache = None
        self.request = request
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
                (
                    "Email for this account not confirmed. Confirmation link was sent to your"
                    " email during registration."
                ),
            )
        if not self.user_cache.is_active:
            self.add_error(
                None,
                "This account is inactive",
            )

    def invalid_login_error(self):
        self.add_error(
            None,
            (
                "Please enter a correct email and password. Note that both fields may be"
                " case-sensitive."
            ),
        )


class ResetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["new_password1"].widget.attrs.update({"placeholder": "New Password"})
        self.fields["new_password2"].widget.attrs.update({"placeholder": "Repeat New Password"})
