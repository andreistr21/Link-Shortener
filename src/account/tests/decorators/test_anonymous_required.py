from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from django.urls import reverse

from account.decorators import anonymous_required
from account.models import Profile


class AnonymousRequiredDecoratorTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.request = self.factory.get("/")
        self.request.user = AnonymousUser()

    def test_anonymous_user_access(self):
        @anonymous_required
        def mock_view(request):
            return HttpResponse("Success!")

        resp = mock_view(self.request)

        self.assertEqual(resp.content, b"Success!")

    def test_logged_in_user_is_redirected(self):
        @anonymous_required
        def mock_view(request):
            return HttpResponse("Success!")

        user = Profile.objects.create_user("test@gmail.com", "test_password")
        self.client.login(email="test@gmail.com", password="test_password")
        self.request.user = user
        resp = mock_view(self.request)
        resp.client = self.client

        self.assertRedirects(resp, reverse("account:overview"))
