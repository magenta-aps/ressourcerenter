from administration.models import Afgiftsperiode, ProduktType, SkemaType, Faktura
from administration.models import BeregningsModel2021
from administration.models import Prisme10QBatch
from datetime import date
from decimal import Decimal
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core import management
from django.test import TransactionTestCase
from django.test import override_settings
from django.urls import reverse
from indberetning.models import Virksomhed, Indberetning, IndberetningLinje
from unittest.mock import patch


class PrismeTestCase(TransactionTestCase):

    def setUp(self) -> None:
        management.call_command('create_initial_dataset')
        self.username = 'test'
        self.user = get_user_model().objects.create_user(username=self.username)
        self.password = 'test'
        self.user.set_password(self.password)
        administration_group, _ = Group.objects.get_or_create(name='administration')
        self.user.save()
        self.user.groups.add(administration_group)

        self.skematyper = {s.id: s for s in SkemaType.objects.all()}
        self.virksomhed = Virksomhed.objects.create(cvr=1234)
        self.beregningsmodel = BeregningsModel2021.objects.create(navn='TestBeregningsModel')
        self.periode = Afgiftsperiode.objects.create(beregningsmodel=self.beregningsmodel, navn_dk='testperiode', dato_fra=date(2022, 1, 1), dato_til=date(2022, 3, 31))

    @override_settings(PRISME_PUSH={**settings.PRISME_PUSH, 'mock': True})
    def test_fakturacreateview_notloggedin(self):
        indberetning = Indberetning.objects.create(afgiftsperiode=self.periode, skematype=self.skematyper[1], virksomhed=self.virksomhed)
        linje = IndberetningLinje.objects.create(indberetning=indberetning, produkttype=ProduktType.objects.get(navn_dk='Makrel, ikke-grønlandsk fartøj'), levende_vægt=1000, salgspris=10000)
        response = self.client.post(reverse('administration:faktura-create', kwargs={'pk': linje.pk}), {'betalingsdato': '2022-03-18'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('administration:login') + "?next=" + reverse('administration:faktura-create', kwargs={'pk': linje.pk}))

    @override_settings(PRISME_PUSH={**settings.PRISME_PUSH, 'mock': True})
    @patch.object(Prisme10QBatch, 'completion_statuses', {
        '10q_production': Prisme10QBatch.STATUS_DELIVERED,
        '10q_development': Prisme10QBatch.STATUS_DELIVERED
    })
    def test_fakturacreateview(self):
        indberetning = Indberetning.objects.create(afgiftsperiode=self.periode, skematype=self.skematyper[1], virksomhed=self.virksomhed)
        linje = IndberetningLinje.objects.create(indberetning=indberetning, produkttype=ProduktType.objects.get(navn_dk='Makrel, ikke-grønlandsk fartøj'), levende_vægt=1000, salgspris=10000)
        self.assertTrue(self.client.login(username=self.username, password=self.password))
        response = self.client.post(reverse('administration:faktura-create', kwargs={'pk': linje.pk}), {'betalingsdato': '2022-03-18'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('administration:indberetningslinje-list'))

        linje.refresh_from_db()
        self.assertEqual(linje.faktura.batch.status, 'delivered')

    @override_settings(PRISME_PUSH={**settings.PRISME_PUSH, 'mock': True})
    def test_fakturasendview_notloggedin(self):
        management.call_command('create_initial_dataset')

        indberetning = Indberetning.objects.create(afgiftsperiode=self.periode, skematype=self.skematyper[1], virksomhed=self.virksomhed)
        linje = IndberetningLinje.objects.create(indberetning=indberetning, produkttype=ProduktType.objects.get(navn_dk='Makrel, ikke-grønlandsk fartøj'), levende_vægt=1000, salgspris=10000)
        batch = Prisme10QBatch.objects.create(oprettet_af=self.user)
        faktura = Faktura.objects.create(batch=batch, virksomhed=self.virksomhed, beløb=Decimal(200), betalingsdato=date(2022, 7, 1), kode=123, opretter=self.user, periode=self.periode, linje=linje,)
        linje.faktura = faktura
        linje.save()

        response = self.client.post(reverse('administration:faktura-send', kwargs={'pk': faktura.pk}), {'destination': '10q_development'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('administration:login') + "?next=" + reverse('administration:faktura-send', kwargs={'pk': faktura.pk}))

    @override_settings(PRISME_PUSH={**settings.PRISME_PUSH, 'mock': True})
    @patch.object(Prisme10QBatch, 'completion_statuses', {
        '10q_production': Prisme10QBatch.STATUS_DELIVERED,
        '10q_development': Prisme10QBatch.STATUS_DELIVERED
    })
    def test_fakturasendview(self):
        management.call_command('create_initial_dataset')

        indberetning = Indberetning.objects.create(afgiftsperiode=self.periode, skematype=self.skematyper[1], virksomhed=self.virksomhed)
        linje = IndberetningLinje.objects.create(indberetning=indberetning, produkttype=ProduktType.objects.get(navn_dk='Makrel, ikke-grønlandsk fartøj'), levende_vægt=1000, salgspris=10000)
        batch = Prisme10QBatch.objects.create(oprettet_af=self.user)
        faktura = Faktura.objects.create(batch=batch, virksomhed=self.virksomhed, beløb=Decimal(200), betalingsdato=date(2022, 7, 1), kode=123, opretter=self.user, periode=self.periode, linje=linje,)

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
