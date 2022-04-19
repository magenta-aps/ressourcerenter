from administration.models import Afgiftsperiode, ProduktType, SkemaType
from administration.models import BeregningsModel2021
from administration.models import G69Code
from datetime import date
from django.contrib.auth import get_user_model
from django.core import management
from django.test import TransactionTestCase
from indberetning.models import Indhandlingssted
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


class G69KodeTestCase(TransactionTestCase):

    def setUp(self):
        super().setUpClass()
        management.call_command("create_initial_dataset")
        self.skematyper = {s.id: s for s in SkemaType.objects.all()}
        self.user = get_user_model().objects.create(username="TestUser")

    def test_get_kode(self):
        sted = Indhandlingssted.objects.first()
        virksomhed = Virksomhed.objects.create(cvr=1234, sted=sted)
        beregningsmodel = BeregningsModel2021.objects.create(navn="TestBeregningsModel")
        periode = Afgiftsperiode.objects.get(dato_fra=date(2022, 1, 1))
        periode.beregningsmodel = beregningsmodel

        skematype_havgående = 1
        skematype_indhandling = 2
        skematype_kystnær = 3

        for navn, skematype_id, expected_kode in (
                ("Hellefisk", skematype_havgående, 10011),
                ("Hellefisk - Hel fisk", 1, 10011),
                ("Hellefisk", skematype_indhandling, 10013),
                ("Hellefisk", skematype_kystnær, 10012),
                ("Makrel, grønlandsk fartøj", skematype_havgående, 10021),
                ("Makrel, grønlandsk fartøj", skematype_indhandling, 10021),
                ("Makrel, ikke-grønlandsk fartøj", skematype_havgående, 10022),
                ("Makrel, ikke-grønlandsk fartøj", skematype_indhandling, 10022),
                ("Lodde, grønlandsk fartøj", skematype_havgående, 10025),
                ("Lodde, grønlandsk fartøj", skematype_indhandling, 10025),
                ("Lodde, ikke-grønlandsk fartøj", skematype_havgående, 10026),
                ("Lodde, ikke-grønlandsk fartøj", skematype_indhandling, 10026),
                ("Torsk", skematype_havgående, 10027),
                ("Torsk", skematype_indhandling, 10028),
                ("Rødfisk", skematype_havgående, 10029),
                ("Rødfisk", skematype_indhandling, 10030),
                ("Kuller", skematype_havgående, 10031),
                ("Kuller", skematype_indhandling, 10032),
                ("Sej", skematype_havgående, 10033),
                ("Sej", skematype_indhandling, 10034),
                ("Blåhvilling, grønlandsk fartøj", skematype_havgående, 10038),
                ("Blåhvilling, grønlandsk fartøj", skematype_indhandling, 10038),
                ("Blåhvilling, ikke-grønlandsk fartøj", skematype_havgående, 10039),
                ("Blåhvilling, ikke-grønlandsk fartøj", skematype_indhandling, 10039),
                ("Guldlaks, grønlandsk fartøj", skematype_havgående, 10040),
                ("Guldlaks, grønlandsk fartøj", skematype_indhandling, 10040),
                ("Guldlaks, ikke-grønlandsk fartøj", skematype_havgående, 10041),
                ("Guldlaks, ikke-grønlandsk fartøj", skematype_indhandling, 10041),
        ):
            produkttype = ProduktType.objects.get(navn_dk=navn)
            expected_full_kode = '0' + '22' + str(sted.stedkode).zfill(4) + \
                                 str(produkttype.fiskeart.kode).zfill(2) + str(expected_kode).zfill(6)
            linje = IndberetningLinje.objects.create(
                indberetning=Indberetning.objects.create(
                    afgiftsperiode=periode,
                    skematype=self.skematyper[skematype_id],
                    virksomhed=virksomhed
                ),
                produkttype=produkttype,
                levende_vægt=1000,
                salgspris=10000,
                indhandlingssted=sted,
            )
            self.assertEqual(G69Code.find_by_indberetningslinje(linje).kode, expected_full_kode, navn)
