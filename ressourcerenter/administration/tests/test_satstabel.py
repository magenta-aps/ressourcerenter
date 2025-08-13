from administration.models import Afgiftsperiode
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse


class PrismeTestCase(TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.username = "test"
        self.user = get_user_model().objects.create_user(username=self.username)
        self.password = "test"
        self.user.set_password(self.password)
        administration_group, _ = Group.objects.get_or_create(name="administration")
        self.user.save()
        self.user.groups.add(administration_group)

    def test_satstabel_update(self):
        self.client.login(username=self.username, password=self.password)
        afgiftsperiode = Afgiftsperiode.objects.first()
        r = self.client.get(
            reverse(
                "administration:afgiftsperiode-satstabel",
                kwargs={"pk": afgiftsperiode.pk},
            )
        )
        self.assertEqual(r.status_code, 200)

        entries = afgiftsperiode.entries.filter(skematype__enabled=True)
        count = entries.count()

        data = {
            "really_submit": [""],
            "entries-TOTAL_FORMS": str(count),
            "entries-INITIAL_FORMS": str(count),
            "entries-MIN_NUM_FORMS": "0",
            "entries-MAX_NUM_FORMS": "1000",
        }
        for index, satstabelelement in enumerate(entries):
            data.update(
                {
                    f"entries-{index}-id": [str(satstabelelement.pk)],
                    f"entries-{index}-skematype": ["1"],
                    f"entries-{index}-fiskeart": [str(satstabelelement.fiskeart.pk)],
                    f"entries-{index}-fartoej_groenlandsk": [""],
                    f"entries-{index}-rate_pr_kg": [""],
                }
            )

        r = self.client.post(
            reverse(
                "administration:afgiftsperiode-satstabel",
                kwargs={"pk": afgiftsperiode.pk},
            ),
            data,
        )
        self.assertEqual(r.status_code, 302)
