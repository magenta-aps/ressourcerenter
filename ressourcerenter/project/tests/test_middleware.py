from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase, override_settings
from django.urls import reverse
from indberetning.models import Virksomhed


@override_settings(
    LOGIN_PROVIDER_CLASS="django_mitid_auth.saml.oiosaml.OIOSaml",
    LOGIN_BYPASS_ENABLED=False,
)
class TestNotLoggedIn(TestCase):
    def test_administration_not_logged_in(self):
        """
        Not logged in user trying to access the administration app gets redirect to the login page for the administration
        """
        r = self.client.get(reverse("administration:frontpage"), follow=True)
        self.assertRedirects(
            r,
            reverse("administration:login")
            + "?next="
            + reverse("administration:frontpage"),
        )
        self.assertEqual(r.status_code, 200)

    def test_user_not_logged_in(self):
        """
        Test citizen trying to access the frontpage, should redirect to the login page
        """
        r = self.client.get(reverse("indberetning:frontpage"))
        self.assertEqual(r.status_code, 302)


@override_settings(
    LOGIN_PROVIDER_CLASS="django_mitid_auth.saml.oiosaml.OIOSaml",
    LOGIN_BYPASS_ENABLED=False,
)
class AdministratorTestCase(TestCase):
    def setUp(self) -> None:
        administration_group, _ = Group.objects.get_or_create(name="administration")
        statistik_group, _ = Group.objects.get_or_create(name="statistik")
        self.username = "test"
        self.user = get_user_model().objects.create_user(username=self.username)
        self.password = "1234"
        self.user.set_password(self.password)
        self.user.groups.add(administration_group, statistik_group)
        self.user.save()

    def test_logged_in_frontpage(self):
        """
        Logged in user tries to access the frontpage.
        """
        self.client.login(username=self.username, password=self.password)
        r = self.client.get(reverse("administration:frontpage"))
        self.assertEqual(r.status_code, 200)

    def test_logged_in_statistik(self):
        """
        Logged in user tries to access the statistics page.
        """
        self.client.login(username=self.username, password=self.password)
        r = self.client.get(reverse("statistik:frontpage"))
        self.assertEqual(r.status_code, 200)

    def test_not_existing(self):
        self.client.login(username=self.username, password=self.password)
        r = self.client.get("/administration/something/login/")
        self.assertEqual(r.status_code, 404)


@override_settings(
    LOGIN_PROVIDER_CLASS="django_mitid_auth.saml.oiosaml.OIOSaml",
    LOGIN_BYPASS_ENABLED=False,
)
class StatistikTestCase(TestCase):
    def setUp(self) -> None:
        statistik_group, _ = Group.objects.get_or_create(name="statistik")
        self.username = "test"
        self.user = get_user_model().objects.create_user(username=self.username)
        self.password = "1234"
        self.user.set_password(self.password)
        self.user.groups.add(statistik_group)
        self.user.save()

    def test_logged_in_frontpage(self):
        """
        Logged in user tries to access the frontpage.
        """
        self.client.login(username=self.username, password=self.password)
        r = self.client.get(reverse("administration:frontpage"))
        self.assertEqual(r.status_code, 403)

    def test_logged_in_statistik(self):
        """
        Logged in user tries to access the statistics page.
        """
        self.client.login(username=self.username, password=self.password)
        r = self.client.get(reverse("statistik:frontpage"))
        self.assertEqual(r.status_code, 200)

    def test_not_existing(self):
        self.client.login(username=self.username, password=self.password)
        r = self.client.get("/administration/something/login/")
        self.assertEqual(r.status_code, 404)


@override_settings(
    DAFO={"mock": True},
    LOGIN_PROVIDER_CLASS="django_mitid_auth.saml.oiosaml.OIOSaml",
    LOGIN_BYPASS_ENABLED=False,
)
class UserTestCase(TestCase):
    def setUp(self) -> None:
        self.cvr = "12345678"
        session = self.client.session
        session["user_info"] = {
            "cvr": self.cvr,
            "organizationname": "Aperture Science Test Facility",
        }
        session.save()

    def tearDown(self) -> None:
        for key in ("user_info",):
            if key in self.client.session:
                del self.client.session[key]

    def test_logged_in_frontpage(self):
        """
        User is "logged in" and can access the frontpage, but gets redirected to the company edit page.
        """
        r = self.client.get(reverse("indberetning:frontpage"), follow=True)
        company = Virksomhed.objects.get(cvr=self.client.session["user_info"]["cvr"])
        self.assertRedirects(
            r, reverse("indberetning:company-edit", kwargs={"pk": company.pk})
        )
        self.assertEqual(200, r.status_code)

    def test_not_existing(self):
        r = self.client.get("/something/login/")
        self.assertEqual(r.status_code, 404)

    def test_logged_in_administration(self):
        """
        Logged in user tries to access the admin page.
        """
        r = self.client.get(reverse("administration:frontpage"))
        self.assertEqual(r.status_code, 302)
