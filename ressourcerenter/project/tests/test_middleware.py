from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings


@override_settings(OPENID={'mock': 'cvr'})
class TestNotLoggedIn(TestCase):

    def test_administration_not_logged_in(self):
        """
        Not logged in user trying to access the administration app gets redirect to the login page for the administration
        """
        r = self.client.get(reverse('administration:frontpage'), follow=True)
        self.assertRedirects(r, reverse('administration:login')+'?next='+reverse('administration:frontpage'))
        self.assertEqual(r.status_code, 200)

    def test_user_not_logged_in(self):
        """
        Test citizen trying to access the frontpage, should redirect to the login page
        """
        r = self.client.get(reverse('indberetning:frontpage'))
        self.assertEqual(r.status_code, 302)


@override_settings(OPENID={'mock': 'cvr'})
class AdministratorTestCase(TestCase):

    def setUp(self) -> None:
        self.username = 'test'
        self.user = get_user_model().objects.create_user(username=self.username)
        self.password = '1234'
        self.user.set_password(self.password)
        self.user.save()

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


class UserTestCase(TestCase):
    """
    using nemId
    """
    def setUp(self) -> None:
        self.client.session['cpr'] = '1234567-4566'

    def tearDown(self) -> None:
        for key in ('cpr', 'cvr'):
            if key in self.client.session:
                del self.client.session[key]

    @override_settings(OPENID={'mock': 'cvr'}, DAFO={'mock': True})
    def test_logged_in_frontpage(self):
        """
        user is "logged in" and can access the frontpage
        :return:
        """
        r = self.client.get(reverse('indberetning:frontpage'), follow=True)
        self.assertEqual(200, r.status_code)

    @override_settings(OPENID={'mock': 'cpr'}, DAFO={'mock': True})
    def test_logged_in_no_cvr_list(self):
        """
        User is logged in but have no active cvr number so it should redirect to company_select
        """
        r = self.client.get(reverse('indberetning:indberetning-list'), follow=True)
        self.assertRedirects(r, reverse('indberetning:company-select'))
        self.assertEqual(200, r.status_code)

    @override_settings(OPENID={'mock': 'cvr'})
    def test_not_existing(self):
        r = self.client.get('/something/login/')
        self.assertEqual(r.status_code, 404)
