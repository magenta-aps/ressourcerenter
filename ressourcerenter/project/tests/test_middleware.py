from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase, override_settings
from indberetning.models import Virksomhed


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
        administration_group, _ = Group.objects.get_or_create(name='administration')
        statistik_group, _ = Group.objects.get_or_create(name='statistik')
        self.username = 'test'
        self.user = get_user_model().objects.create_user(username=self.username)
        self.password = '1234'
        self.user.set_password(self.password)
        self.user.groups.add(administration_group, statistik_group)
        self.user.save()

    def test_logged_in_frontpage(self):
        """
        Logged in user tries to access the frontpage.
        """
        self.client.login(username=self.username, password=self.password)
        r = self.client.get(reverse('administration:frontpage'))
        self.assertEqual(r.status_code, 200)

    def test_logged_in_statistik(self):
        """
        Logged in user tries to access the statistics page.
        """
        self.client.login(username=self.username, password=self.password)
        r = self.client.get(reverse('statistik:frontpage'))
        self.assertEqual(r.status_code, 200)

    def test_not_existing(self):
        self.client.login(username=self.username, password=self.password)
        r = self.client.get('/something/login/')
        self.assertEqual(r.status_code, 404)


@override_settings(OPENID={'mock': 'cvr'})
class StatistikTestCase(TestCase):

    def setUp(self) -> None:
        statistik_group, _ = Group.objects.get_or_create(name='statistik')
        self.username = 'test'
        self.user = get_user_model().objects.create_user(username=self.username)
        self.password = '1234'
        self.user.set_password(self.password)
        self.user.groups.add(statistik_group)
        self.user.save()

    def test_logged_in_frontpage(self):
        """
        Logged in user tries to access the frontpage.
        """
        self.client.login(username=self.username, password=self.password)
        r = self.client.get(reverse('administration:frontpage'))
        self.assertEqual(r.status_code, 403)

    def test_logged_in_statistik(self):
        """
        Logged in user tries to access the statistics page.
        """
        self.client.login(username=self.username, password=self.password)
        r = self.client.get(reverse('statistik:frontpage'))
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
        self.cvr = '12345678'
        self.client.session['cvr'] = self.cvr

    def tearDown(self) -> None:
        for key in ('cpr', 'cvr'):
            if key in self.client.session:
                del self.client.session[key]

    @override_settings(OPENID={'mock': 'cvr'}, DAFO={'mock': True})
    def test_logged_in_frontpage(self):
        """
        User is "logged in" and can access the frontpage, but gets redirected to the company edit page.
        """
        r = self.client.get(reverse('indberetning:frontpage'), follow=True)
        company = Virksomhed.objects.get(cvr=self.client.session['cvr'])
        self.assertRedirects(r, reverse('indberetning:company-edit', kwargs={'pk': company.pk}))
        self.assertEqual(200, r.status_code)

    @override_settings(OPENID={'mock': 'cvr'}, DAFO={'mock': True})
    def test_logged_in_cvr_exists(self):
        """
        User is not logged in so redirect to the login page
        """
        Virksomhed.objects.create(cvr=self.cvr)
        r = self.client.get(reverse('indberetning:indberetning-list'), follow=True)
        self.assertRedirects(r, reverse('indberetning:indberetning-list'))
        self.assertEqual(200, r.status_code)

    @override_settings(OPENID={'mock': 'cvr'})
    def test_not_existing(self):
        r = self.client.get('/something/login/')
        self.assertEqual(r.status_code, 404)

    @override_settings(OPENID={'mock': 'cvr'})
    def test_logged_in_administration(self):
        """
        Logged in user tries to access the admin page.
        """
        r = self.client.get(reverse('administration:frontpage'))
        self.assertEqual(r.status_code, 302)
