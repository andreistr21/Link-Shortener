from django.shortcuts import get_object_or_404
from .models import Profile


def get_profile(pk):
    return get_object_or_404(Profile, pk=pk)

def get_profile_by_email(email):
    return get_object_or_404(Profile, email=email)