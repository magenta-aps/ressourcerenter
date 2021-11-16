from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings


@override_settings(OPENID={'mock': True})
class AdministratorTestCase(TestCase):

    def setUp(self) -> None:
        self.username = 'test'
        self.user = get_user_model().objects.create_user(username=self.username)
        self.password = '1234'
        self.user.set_password(self.password)
        self.user.save()

    def test_not_logged_in(self):
        """
        Not logged in user trying to access the administration app gets redirect to the login page for the administration
        """
        r = self.client.get(reverse('administration:frontpage'), follow=True)
        self.assertRedirects(r, reverse('administration:login')+'?next='+reverse('administration:frontpage'))
        self.assertEqual(r.status_code, 200)

    def test_logged_in_frontpage(self):
        """
        Logged in user tries to access the frontpage.
        """
        self.client.login(username=self.username, password=self.password)
        r = self.client.get(reverse('administration:frontpage'))
        self.assertEqual(r.status_code, 200)

    def test_not_existing(self):
        self.client.login(username=self.username, password=self.password)
        r = self.client.get('/something/login/')
        self.assertEqual(r.status_code, 404)


@override_settings(OPENID={'mock': True})
class UserTestCase(TestCase):
    """
    using nemId
    """
    def tearDown(self) -> None:
        if 'cpr' in self.client.session:
            del self.client.session['cpr']

    def test_logged_in_frontpage(self):
        """
        user is "logged in" and can access the frontpage
        :return:
        """
        self.client.session['cpr'] = '1234567-4566'
        r = self.client.get(reverse('indberetning:frontpage'), follow=True)
        self.assertEqual(200, r.status_code)

    def test_not_existing(self):
        self.client.session['cpr'] = '1234567-4566'
        r = self.client.get('/something/login/')
        self.assertEqual(r.status_code, 404)
