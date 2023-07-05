from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponseRedirect,
    QueryDict,
)
from django.shortcuts import redirect, render
from django.urls import reverse

from account.decorators import anonymous_required
from account.forms import SignInForm, SignUpForm
from account.selectors import get_links_by_user, get_links_total_clicks
from account.services import (
    check_user_access,
    get_domain,
    get_link_datasets,
    get_links_and_clicks,
    map_clicks_amount_to_link,
    remove_link,
    rename_redis_list,
    send_new_activation_link,
    sign_in_user,
    sign_up_user,
    update_email_confirmation_status,
)
from shortener.forms import ShortenForm
from shortener.selectors import get_link
from shortener.services import short_link

from account._temp import populate_redis_with_test_data


@anonymous_required
def sign_up(request):
    sign_up_form = SignUpForm()
    if request.POST:
        sign_up_form = SignUpForm(request.POST)
        if http_response_redirect := sign_up_user(request, sign_up_form):
            return http_response_redirect

    return render(
        request,
        "account/sign_up.html",
        {
            "sign_up_form": sign_up_form,
        },
    )


@anonymous_required
def sign_in(request):
    new_activation_link = False
    sign_in_form = SignInForm()
    if request.POST:
        sign_in_form = SignInForm(request, request.POST)
        resp = sign_in_user(request, sign_in_form)
        if type(resp) is HttpResponseRedirect:
            return resp
        elif resp == "Error":
            new_activation_link = True

    return render(
        request,
        "account/sign_in.html",
        {
            "sign_in_form": sign_in_form,
            "new_activation_link": new_activation_link,
        },
    )


def confirm_email(request):
    return render(request, "account/confirm_email.html")


@anonymous_required
def activate_email(_, uidb64, token):
    update_email_confirmation_status(uidb64, token)

    return redirect(reverse("account:sign_in"))


@login_required
def overview(request: HttpRequest) -> HttpResponse:
    links = get_links_by_user(request.user)
    total_clicks = 0
    mapped_links = []
    if links:
        total_clicks = get_links_total_clicks(links)
        mapped_links = map_clicks_amount_to_link(links[:3])
    view_more = len(links) > 3
    domain = get_domain()

    return render(
        request,
        "account/overview.html",
        {
            "total_clicks": total_clicks,
            "mapped_links": mapped_links,
            "view_more": view_more,
            "domain": domain,
        },
    )


@anonymous_required
def new_confirmation_link(request: HttpRequest) -> HttpResponse:
    """Sending new confirmation link to email"""
    new_confirmation_link_form = SignInForm()
    if request.POST:
        new_confirmation_link_form = SignInForm(request, request.POST)
        if http_resp_redirect := send_new_activation_link(
            request, new_confirmation_link_form
        ):
            return http_resp_redirect

    return render(
        request,
        "account/new_confirmation_link.html",
        {
            "new_confirmation_link_form": new_confirmation_link_form,
        },
    )


@login_required
def links_list(request: HttpRequest, page: int = 1) -> HttpResponse:
    current_query_str = request.META.get("QUERY_STRING")
    current_query_dict = QueryDict(current_query_str)
    domain = get_domain()

    mapped_links = get_links_and_clicks(request)

    paginator = None
    page_obj = None
    elided_page_range = None
    if mapped_links:
        paginator = Paginator(mapped_links, settings.LINKS_ITEMS_PER_PAGE)
        page_obj = paginator.get_page(page)
        elided_page_range = paginator.get_elided_page_range(
            page_obj.number, on_each_side=3, on_ends=1
        )

    return render(
        request,
        "account/links_list.html",
        {
            "domain": domain,
            "page_obj": page_obj,
            "elided_page_range": elided_page_range,
            "current_query_str": current_query_str,
            "current_query_dict": current_query_dict,
        },
    )


@login_required
def link_statistics(request: HttpRequest, alias: str) -> HttpResponse:
    link = get_link(alias)
    check_user_access(request.user, link)
    domain = get_domain()
    clicks_chart_dataset, country_chart_dataset = get_link_datasets(link)

    return render(
        request,
        "account/link_statistics.html",
        {
            "link": link,
            "domain": domain,
            "clicks_chart_dataset": clicks_chart_dataset,
            "country_chart_dataset": country_chart_dataset,
        },
    )


@login_required
def update_link(request: HttpRequest, alias: str) -> HttpResponse:
    link = get_link(alias)
    check_user_access(request.user, link)
    if request.POST:
        update_link_form = ShortenForm(request.POST, instance=link)
        if update_link_form.is_valid():
            old_alias = alias
            alias = short_link(request, update_link_form, link)
            if not update_link_form.errors:
                if old_alias != alias:
                    rename_redis_list(old_alias, alias)

                return redirect(
                    reverse("account:link_statistics", args=(alias,))
                )
    else:
        update_link_form = ShortenForm(instance=link)

    return render(
        request,
        "account/update_link.html",
        {
            "update_link_form": update_link_form,
        },
    )


@login_required
def delete_link(request: HttpRequest, alias: str) -> HttpResponse:
    link = get_link(alias)
    check_user_access(request.user, link)
    remove_link(link)

    return redirect(reverse("account:links_list"))
