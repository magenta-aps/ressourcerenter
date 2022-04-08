from administration.models import Afgiftsperiode, ProduktType, SkemaType
from administration.models import BeregningsModel2021
from datetime import date
from django.contrib.auth import get_user_model
from django.core import management
from django.test import TransactionTestCase
from indberetning.models import Virksomhed, Indberetning, IndberetningLinje


class FangsttypeTestCase(TransactionTestCase):
    def setUp(self):
        super().setUpClass()
        management.call_command("create_initial_dataset")
        self.skematyper = {s.id: s for s in SkemaType.objects.all()}
        self.user = get_user_model().objects.create(username="TestUser")

    def test_fangsttyper(self):

        virksomhed = Virksomhed.objects.create(cvr=1234)
        beregningsmodel = BeregningsModel2021.objects.create(navn="TestBeregningsModel")
        periode = Afgiftsperiode.objects.get(dato_fra=date(2022, 1, 1))
        periode.beregningsmodel = beregningsmodel

        indberetning1 = Indberetning.objects.create(
            afgiftsperiode=periode, skematype=self.skematyper[1], virksomhed=virksomhed
        )
        for navn in [
            "Makrel",
            "Sild",
            "Lodde",
            "Blåhvilling",
            "Guldlaks",
            "Hellefisk",
            "Torsk",
            "Kuller",
            "Sej",
            "Rødfisk",
            "Reje - havgående licens",
        ]:
            for produkttype in ProduktType.objects.filter(navn_dk__startswith=navn):
                linje = IndberetningLinje.objects.create(
                    indberetning=indberetning1,
                    produkttype=produkttype,
                    levende_vægt=1000,
                    salgspris=10000,
                )
                self.assertEqual(linje.fangsttype, "havgående", produkttype.navn_dk)

        indberetning2 = Indberetning.objects.create(
            afgiftsperiode=periode, skematype=self.skematyper[2], virksomhed=virksomhed
        )
        for navn in [
            "Makrel",
            "Sild",
            "Lodde",
            "Blåhvilling",
            "Guldlaks",
            "Hellefisk",
            "Torsk",
            "Kuller",
            "Sej",
            "Rødfisk",
        ]:
            for produkttype in ProduktType.objects.filter(navn_dk__startswith=navn):
                linje = IndberetningLinje.objects.create(
                    indberetning=indberetning2,
                    produkttype=produkttype,
                    levende_vægt=1000,
                    salgspris=10000,
                )
                self.assertEqual(linje.fangsttype, "indhandling", produkttype.navn_dk)

        indberetning3 = Indberetning.objects.create(
            afgiftsperiode=periode, skematype=self.skematyper[3], virksomhed=virksomhed
        )
        for navn in [
            "Makrel",
            "Sild",
            "Lodde",
            "Blåhvilling",
            "Guldlaks",
            "Hellefisk",
            "Torsk",
            "Kuller",
            "Sej",
            "Rødfisk",
            "Reje - kystnær licens",
        ]:
            for produkttype in ProduktType.objects.filter(navn_dk__startswith=navn):
                linje = IndberetningLinje.objects.create(
                    indberetning=indberetning3,
                    produkttype=produkttype,
                    levende_vægt=1000,
                    salgspris=10000,
                )
                self.assertEqual(linje.fangsttype, "kystnært", produkttype.navn_dk)

        indberetning4 = Indberetning.objects.create(
            afgiftsperiode=periode, skematype=self.skematyper[1], virksomhed=virksomhed
        )
        navn = "Reje - Svalbard og Barentshavet"
        for produkttype in ProduktType.objects.filter(navn_dk__startswith=navn):
            linje = IndberetningLinje.objects.create(
                indberetning=indberetning4,
                produkttype=produkttype,
                levende_vægt=1000,
                salgspris=10000,
            )
            self.assertEqual(linje.fangsttype, "svalbard", produkttype.navn_dk)
