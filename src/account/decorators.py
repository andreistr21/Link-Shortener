import functools
from django.shortcuts import redirect
from django.urls import reverse


def anonymous_required(view_func, redirect_url="account:overview"):
    """
    this decorator ensures that a user is not logged in,
    if a user is logged in, the user will get redirected to
    the url whose view name was passed to the redirect_url parameter
    """

    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return view_func(request, *args, **kwargs)
        return redirect(reverse(redirect_url))

    return wrapper
