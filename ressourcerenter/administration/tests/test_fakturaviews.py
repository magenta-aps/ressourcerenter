from administration.management.commands.create_initial_dataset import Command as CreateInitialDatasetCommand
from administration.models import Afgiftsperiode, FiskeArt, ProduktType, SkemaType, Faktura
from datetime import date
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.test import TransactionTestCase
from indberetning.models import Virksomhed, Indberetning, IndberetningLinje
from django.urls import reverse
from django.contrib.auth.models import Group

from django.test import override_settings
from administration.models import Prisme10QBatch
from django.conf import settings
from unittest.mock import patch


class PrismeTestCase(TransactionTestCase):

    def setUp(self) -> None:
        CreateInitialDatasetCommand().handle()
        self.username = 'test'
        self.user = get_user_model().objects.create_user(username=self.username)
        self.password = 'test'
        self.user.set_password(self.password)
        administration_group, _ = Group.objects.get_or_create(name='administration')
        self.user.save()
        self.user.groups.add(administration_group)

        self.skematyper = {s.id: s for s in SkemaType.objects.all()}
        self.virksomhed = Virksomhed.objects.create(cvr=1234)
        self.periode = Afgiftsperiode.objects.create(navn_dk='testperiode', dato_fra=date(2022, 1, 1), dato_til=date(2022, 3, 31))


    @override_settings(PRISME_PUSH={**settings.PRISME_PUSH, 'do_send': False})
    @patch.object(Prisme10QBatch, 'completion_statuses', {
        '10q_production': Prisme10QBatch.STATUS_DELIVERED,
        '10q_development': Prisme10QBatch.STATUS_DELIVERED
    })
    def test_fakturasendview(self):
        CreateInitialDatasetCommand().handle()

        indberetning = Indberetning.objects.create(afgiftsperiode=self.periode, skematype=self.skematyper[1], virksomhed=self.virksomhed)
        linje = IndberetningLinje.objects.create(indberetning=indberetning, produkttype=ProduktType.objects.get(navn_dk='Makrel, ikke-grønlandsk fartøj'), levende_vægt=1000, salgspris=10000)
        batch = Prisme10QBatch.objects.create(oprettet_af=self.user)
        faktura = Faktura.objects.create(
            batch=batch,
            virksomhed=self.virksomhed,
            beløb=Decimal(200),
            betalingsdato=date(2022, 7, 1),
            kode=123,
            opretter=self.user,
            periode=self.periode,
            linje=linje,
        )
        linje.faktura = faktura
        linje.save()

        response = self.client.post(reverse('administration:faktura-send', kwargs={'pk': faktura.pk}), {'destination': '10q_development'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('administration:login') + "?next=" + reverse('administration:faktura-send', kwargs={'pk': faktura.pk}))

        self.assertTrue(self.client.login(username=self.username, password=self.password))
        response = self.client.post(reverse('administration:faktura-send', kwargs={'pk': faktura.pk}), {'destination': '10q_development'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('administration:faktura-detail', kwargs={'pk': faktura.pk}))

        batch.refresh_from_db()
        self.assertEqual(batch.status, 'delivered')
