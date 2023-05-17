from django import forms

from shortener.models import Link


class ShortenForm(forms.ModelForm):
    class Meta:
        model = Link
        fields = (
            "long_link",
            "alias",
        )
        widgets = {
            "long_link": forms.TextInput(
                attrs={"placeholder": "Enter a long link to make a short one", "autofocus": True}
            ),
            "alias": forms.TextInput(attrs={"placeholder": "Alias (Optional)"}),
        }
