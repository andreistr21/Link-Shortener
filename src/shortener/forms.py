from django import forms

from shortener.models import Link


class ShortenForm(forms.ModelForm):
    alias = forms.CharField(required=False, widget=forms.TextInput(attrs={"placeholder": "Alias (Optional)"}))

    class Meta:
        model = Link
        fields = ("long_link",)
        widgets = {
            "long_link": forms.TextInput(
                attrs={"placeholder": "Enter a long link to make a short one", "autofocus": True}
            ),
        }
