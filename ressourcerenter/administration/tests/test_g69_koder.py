from administration.models import Afgiftsperiode, ProduktType, SkemaType
from administration.models import BeregningsModel2021
from administration.models import G69Code
from datetime import date
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core import management
from django.test import TransactionTestCase
from django.urls import reverse
from indberetning.models import Indhandlingssted
from indberetning.models import Virksomhed, Indberetning, IndberetningLinje
from openpyxl import load_workbook
from io import BytesIO


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
        self.username = 'test'
        self.user = get_user_model().objects.create_user(username=self.username)
        self.password = 'test'
        self.user.set_password(self.password)
        administration_group, _ = Group.objects.get_or_create(name='administration')
        self.user.save()
        self.user.groups.add(administration_group)

    def test_get_kode(self):
        sted = Indhandlingssted.objects.get(navn='Innaarsuit')
        virksomhed = Virksomhed.objects.create(cvr=1234, stedkode=sted.stedkode)
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
            expected_full_kode = '0' + str(periode.dato_fra.year)[2:] + str(sted.stedkode).zfill(4) + \
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

    def test_get_raw(self):
        expected = {
            'headers': [
                ('kode', 'G69-Kode'), ('skatteår', 'År'), ('fangsttype', 'Fangsttype'),
                ('aktivitet_kode', 'Aktivitetskode'), ('fiskeart_navn', 'Fiskeart'), ('fiskeart_kode', 'Fiskeart kode'),
                ('sted_navn', 'Sted'), ('sted_kode', 'Stedkode'), ('grønlandsk', 'Grønlandsk fartøj')
            ],
            'data': [
                {'kode': '022160704010038', 'skatteår': 2022, 'fangsttype': 'havgående', 'aktivitet_kode': '010038', 'fiskeart_navn': 'Blåhvilling', 'fiskeart_kode': 4, 'sted_navn': 'Innaarsuit', 'sted_kode': 1607, 'grønlandsk': 'Ja'},
                {'kode': '022160704010038', 'skatteår': 2022, 'fangsttype': 'indhandling', 'aktivitet_kode': '010038', 'fiskeart_navn': 'Blåhvilling', 'fiskeart_kode': 4, 'sted_navn': 'Innaarsuit', 'sted_kode': 1607, 'grønlandsk': 'Ja'},
                {'kode': '022160704010038', 'skatteår': 2022, 'fangsttype': 'kystnært', 'aktivitet_kode': '010038', 'fiskeart_navn': 'Blåhvilling', 'fiskeart_kode': 4, 'sted_navn': 'Innaarsuit', 'sted_kode': 1607, 'grønlandsk': 'Ja'},
                {'kode': '022160704010039', 'skatteår': 2022, 'fangsttype': 'havgående', 'aktivitet_kode': '010039', 'fiskeart_navn': 'Blåhvilling', 'fiskeart_kode': 4, 'sted_navn': 'Innaarsuit', 'sted_kode': 1607, 'grønlandsk': 'Nej'},
                {'kode': '022160704010039', 'skatteår': 2022, 'fangsttype': 'indhandling', 'aktivitet_kode': '010039', 'fiskeart_navn': 'Blåhvilling', 'fiskeart_kode': 4, 'sted_navn': 'Innaarsuit', 'sted_kode': 1607, 'grønlandsk': 'Nej'},
                {'kode': '022160704010039', 'skatteår': 2022, 'fangsttype': 'kystnært', 'aktivitet_kode': '010039', 'fiskeart_navn': 'Blåhvilling', 'fiskeart_kode': 4, 'sted_navn': 'Innaarsuit', 'sted_kode': 1607, 'grønlandsk': 'Nej'},
                {'kode': '022160705010040', 'skatteår': 2022, 'fangsttype': 'havgående', 'aktivitet_kode': '010040', 'fiskeart_navn': 'Guldlaks', 'fiskeart_kode': 5, 'sted_navn': 'Innaarsuit', 'sted_kode': 1607, 'grønlandsk': 'Ja'},
                {'kode': '022160705010040', 'skatteår': 2022, 'fangsttype': 'indhandling', 'aktivitet_kode': '010040', 'fiskeart_navn': 'Guldlaks', 'fiskeart_kode': 5, 'sted_navn': 'Innaarsuit', 'sted_kode': 1607, 'grønlandsk': 'Ja'},
                {'kode': '022160705010040', 'skatteår': 2022, 'fangsttype': 'kystnært', 'aktivitet_kode': '010040', 'fiskeart_navn': 'Guldlaks', 'fiskeart_kode': 5, 'sted_navn': 'Innaarsuit', 'sted_kode': 1607, 'grønlandsk': 'Ja'},
                {'kode': '022160705010041', 'skatteår': 2022, 'fangsttype': 'havgående', 'aktivitet_kode': '010041', 'fiskeart_navn': 'Guldlaks', 'fiskeart_kode': 5, 'sted_navn': 'Innaarsuit', 'sted_kode': 1607, 'grønlandsk': 'Nej'},
                {'kode': '022160705010041', 'skatteår': 2022, 'fangsttype': 'indhandling', 'aktivitet_kode': '010041', 'fiskeart_navn': 'Guldlaks', 'fiskeart_kode': 5, 'sted_navn': 'Innaarsuit', 'sted_kode': 1607, 'grønlandsk': 'Nej'},
                {'kode': '022160705010041', 'skatteår': 2022, 'fangsttype': 'kystnært', 'aktivitet_kode': '010041', 'fiskeart_navn': 'Guldlaks', 'fiskeart_kode': 5, 'sted_navn': 'Innaarsuit', 'sted_kode': 1607, 'grønlandsk': 'Nej'},
                {'kode': '022160706010011', 'skatteår': 2022, 'fangsttype': 'havgående', 'aktivitet_kode': '010011', 'fiskeart_navn': 'Hellefisk', 'fiskeart_kode': 6, 'sted_navn': 'Innaarsuit', 'sted_kode': 1607, 'grønlandsk': ''},
                {'kode': '022160706010013', 'skatteår': 2022, 'fangsttype': 'indhandling', 'aktivitet_kode': '010013', 'fiskeart_navn': 'Hellefisk', 'fiskeart_kode': 6, 'sted_navn': 'Innaarsuit', 'sted_kode': 1607, 'grønlandsk': ''},
                {'kode': '022160706010012', 'skatteår': 2022, 'fangsttype': 'kystnært', 'aktivitet_kode': '010012', 'fiskeart_navn': 'Hellefisk', 'fiskeart_kode': 6, 'sted_navn': 'Innaarsuit', 'sted_kode': 1607, 'grønlandsk': ''},
                {'kode': '022160708010031', 'skatteår': 2022, 'fangsttype': 'havgående', 'aktivitet_kode': '010031', 'fiskeart_navn': 'Kuller', 'fiskeart_kode': 8, 'sted_navn': 'Innaarsuit', 'sted_kode': 1607, 'grønlandsk': ''},
                {'kode': '022160708010032', 'skatteår': 2022, 'fangsttype': 'indhandling', 'aktivitet_kode': '010032', 'fiskeart_navn': 'Kuller', 'fiskeart_kode': 8, 'sted_navn': 'Innaarsuit', 'sted_kode': 1607, 'grønlandsk': ''},
                {'kode': '022160703010025', 'skatteår': 2022, 'fangsttype': 'havgående', 'aktivitet_kode': '010025', 'fiskeart_navn': 'Lodde', 'fiskeart_kode': 3, 'sted_navn': 'Innaarsuit', 'sted_kode': 1607, 'grønlandsk': 'Ja'},
                {'kode': '022160703010025', 'skatteår': 2022, 'fangsttype': 'indhandling', 'aktivitet_kode': '010025', 'fiskeart_navn': 'Lodde', 'fiskeart_kode': 3, 'sted_navn': 'Innaarsuit', 'sted_kode': 1607, 'grønlandsk': 'Ja'},
                {'kode': '022160703010025', 'skatteår': 2022, 'fangsttype': 'kystnært', 'aktivitet_kode': '010025', 'fiskeart_navn': 'Lodde', 'fiskeart_kode': 3, 'sted_navn': 'Innaarsuit', 'sted_kode': 1607, 'grønlandsk': 'Ja'},
                {'kode': '022160703010026', 'skatteår': 2022, 'fangsttype': 'havgående', 'aktivitet_kode': '010026', 'fiskeart_navn': 'Lodde', 'fiskeart_kode': 3, 'sted_navn': 'Innaarsuit', 'sted_kode': 1607, 'grønlandsk': 'Nej'},
                {'kode': '022160703010026', 'skatteår': 2022, 'fangsttype': 'indhandling', 'aktivitet_kode': '010026', 'fiskeart_navn': 'Lodde', 'fiskeart_kode': 3, 'sted_navn': 'Innaarsuit', 'sted_kode': 1607, 'grønlandsk': 'Nej'},
                {'kode': '022160703010026', 'skatteår': 2022, 'fangsttype': 'kystnært', 'aktivitet_kode': '010026', 'fiskeart_navn': 'Lodde', 'fiskeart_kode': 3, 'sted_navn': 'Innaarsuit', 'sted_kode': 1607, 'grønlandsk': 'Nej'},
                {'kode': '022160701010021', 'skatteår': 2022, 'fangsttype': 'havgående', 'aktivitet_kode': '010021', 'fiskeart_navn': 'Makrel', 'fiskeart_kode': 1, 'sted_navn': 'Innaarsuit', 'sted_kode': 1607, 'grønlandsk': 'Ja'},
                {'kode': '022160701010021', 'skatteår': 2022, 'fangsttype': 'indhandling', 'aktivitet_kode': '010021', 'fiskeart_navn': 'Makrel', 'fiskeart_kode': 1, 'sted_navn': 'Innaarsuit', 'sted_kode': 1607, 'grønlandsk': 'Ja'},
                {'kode': '022160701010021', 'skatteår': 2022, 'fangsttype': 'kystnært', 'aktivitet_kode': '010021', 'fiskeart_navn': 'Makrel', 'fiskeart_kode': 1, 'sted_navn': 'Innaarsuit', 'sted_kode': 1607, 'grønlandsk': 'Ja'},
                {'kode': '022160701010022', 'skatteår': 2022, 'fangsttype': 'havgående', 'aktivitet_kode': '010022', 'fiskeart_navn': 'Makrel', 'fiskeart_kode': 1, 'sted_navn': 'Innaarsuit', 'sted_kode': 1607, 'grønlandsk': 'Nej'},
                {'kode': '022160701010022', 'skatteår': 2022, 'fangsttype': 'indhandling', 'aktivitet_kode': '010022', 'fiskeart_navn': 'Makrel', 'fiskeart_kode': 1, 'sted_navn': 'Innaarsuit', 'sted_kode': 1607, 'grønlandsk': 'Nej'},
                {'kode': '022160701010022', 'skatteår': 2022, 'fangsttype': 'kystnært', 'aktivitet_kode': '010022', 'fiskeart_navn': 'Makrel', 'fiskeart_kode': 1, 'sted_navn': 'Innaarsuit', 'sted_kode': 1607, 'grønlandsk': 'Nej'},
                {'kode': '022160711010011', 'skatteår': 2022, 'fangsttype': 'havgående', 'aktivitet_kode': '010011', 'fiskeart_navn': 'Reje - havgående licens', 'fiskeart_kode': 11, 'sted_navn': 'Innaarsuit', 'sted_kode': 1607, 'grønlandsk': ''},
                {'kode': '022160712010012', 'skatteår': 2022, 'fangsttype': 'kystnært', 'aktivitet_kode': '010012', 'fiskeart_navn': 'Reje - kystnær licens', 'fiskeart_kode': 12, 'sted_navn': 'Innaarsuit', 'sted_kode': 1607, 'grønlandsk': ''},
                {'kode': '022160713010014', 'skatteår': 2022, 'fangsttype': 'svalbard', 'aktivitet_kode': '010014', 'fiskeart_navn': 'Reje - Svalbard og Barentshavet', 'fiskeart_kode': 13, 'sted_navn': 'Innaarsuit', 'sted_kode': 1607, 'grønlandsk': ''},
                {'kode': '022160710010029', 'skatteår': 2022, 'fangsttype': 'havgående', 'aktivitet_kode': '010029', 'fiskeart_navn': 'Rødfisk', 'fiskeart_kode': 10, 'sted_navn': 'Innaarsuit', 'sted_kode': 1607, 'grønlandsk': ''},
                {'kode': '022160710010030', 'skatteår': 2022, 'fangsttype': 'indhandling', 'aktivitet_kode': '010030', 'fiskeart_navn': 'Rødfisk', 'fiskeart_kode': 10, 'sted_navn': 'Innaarsuit', 'sted_kode': 1607, 'grønlandsk': ''},
                {'kode': '022160709010033', 'skatteår': 2022, 'fangsttype': 'havgående', 'aktivitet_kode': '010033', 'fiskeart_navn': 'Sej', 'fiskeart_kode': 9, 'sted_navn': 'Innaarsuit', 'sted_kode': 1607, 'grønlandsk': ''},
                {'kode': '022160709010034', 'skatteår': 2022, 'fangsttype': 'indhandling', 'aktivitet_kode': '010034', 'fiskeart_navn': 'Sej', 'fiskeart_kode': 9, 'sted_navn': 'Innaarsuit', 'sted_kode': 1607, 'grønlandsk': ''},
                {'kode': '022160702010023', 'skatteår': 2022, 'fangsttype': 'havgående', 'aktivitet_kode': '010023', 'fiskeart_navn': 'Sild', 'fiskeart_kode': 2, 'sted_navn': 'Innaarsuit', 'sted_kode': 1607, 'grønlandsk': 'Ja'},
                {'kode': '022160702010023', 'skatteår': 2022, 'fangsttype': 'indhandling', 'aktivitet_kode': '010023', 'fiskeart_navn': 'Sild', 'fiskeart_kode': 2, 'sted_navn': 'Innaarsuit', 'sted_kode': 1607, 'grønlandsk': 'Ja'},
                {'kode': '022160702010023', 'skatteår': 2022, 'fangsttype': 'kystnært', 'aktivitet_kode': '010023', 'fiskeart_navn': 'Sild', 'fiskeart_kode': 2, 'sted_navn': 'Innaarsuit', 'sted_kode': 1607, 'grønlandsk': 'Ja'},
                {'kode': '022160702010024', 'skatteår': 2022, 'fangsttype': 'havgående', 'aktivitet_kode': '010024', 'fiskeart_navn': 'Sild', 'fiskeart_kode': 2, 'sted_navn': 'Innaarsuit', 'sted_kode': 1607, 'grønlandsk': 'Nej'},
                {'kode': '022160702010024', 'skatteår': 2022, 'fangsttype': 'indhandling', 'aktivitet_kode': '010024', 'fiskeart_navn': 'Sild', 'fiskeart_kode': 2, 'sted_navn': 'Innaarsuit', 'sted_kode': 1607, 'grønlandsk': 'Nej'},
                {'kode': '022160702010024', 'skatteår': 2022, 'fangsttype': 'kystnært', 'aktivitet_kode': '010024', 'fiskeart_navn': 'Sild', 'fiskeart_kode': 2, 'sted_navn': 'Innaarsuit', 'sted_kode': 1607, 'grønlandsk': 'Nej'},
                {'kode': '022160707010027', 'skatteår': 2022, 'fangsttype': 'havgående', 'aktivitet_kode': '010027', 'fiskeart_navn': 'Torsk', 'fiskeart_kode': 7, 'sted_navn': 'Innaarsuit', 'sted_kode': 1607, 'grønlandsk': ''},
                {'kode': '022160707010028', 'skatteår': 2022, 'fangsttype': 'indhandling', 'aktivitet_kode': '010028', 'fiskeart_navn': 'Torsk', 'fiskeart_kode': 7, 'sted_navn': 'Innaarsuit', 'sted_kode': 1607, 'grønlandsk': ''}
            ]}
        self.maxDiff = None
        self.assertEqual(G69Code.get_spreadsheet_raw(2022), expected)

    def test_csv(self):
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('administration:g69-download') + '?år=2022')
        self.assertEqual(response.get('Content-Disposition'), "attachment; filename=g69_koder.xlsx")
        wb = load_workbook(filename=BytesIO(response.content))
        ws = wb.active
        self.assertEqual(ws.max_column, 9)
        self.assertEqual(ws.max_row, 25)

        # Koder er unikke og sorterede
        expected = [
            ['G69-Kode', 'År', 'Fangsttype', 'Aktivitetskode', 'Fiskeart', 'Fiskeart kode', 'Sted', 'Stedkode', 'Grønlandsk fartøj'],
            ['022160704010038', 2022, None, '010038', 'Blåhvilling', 4, 'Innaarsuit', 1607, 'Ja'],
            ['022160704010039', 2022, None, '010039', 'Blåhvilling', 4, 'Innaarsuit', 1607, 'Nej'],
            ['022160705010040', 2022, None, '010040', 'Guldlaks', 5, 'Innaarsuit', 1607, 'Ja'],
            ['022160705010041', 2022, None, '010041', 'Guldlaks', 5, 'Innaarsuit', 1607, 'Nej'],
            ['022160706010011', 2022, 'havgående', '010011', 'Hellefisk', 6, 'Innaarsuit', 1607, None],
            ['022160706010013', 2022, 'indhandling', '010013', 'Hellefisk', 6, 'Innaarsuit', 1607, None],
            ['022160706010012', 2022, 'kystnært', '010012', 'Hellefisk', 6, 'Innaarsuit', 1607, None],
            ['022160708010031', 2022, 'havgående', '010031', 'Kuller', 8, 'Innaarsuit', 1607, None],
            ['022160708010032', 2022, 'indhandling', '010032', 'Kuller', 8, 'Innaarsuit', 1607, None],
            ['022160703010025', 2022, None, '010025', 'Lodde', 3, 'Innaarsuit', 1607, 'Ja'],
            ['022160703010026', 2022, None, '010026', 'Lodde', 3, 'Innaarsuit', 1607, 'Nej'],
            ['022160701010021', 2022, None, '010021', 'Makrel', 1, 'Innaarsuit', 1607, 'Ja'],
            ['022160701010022', 2022, None, '010022', 'Makrel', 1, 'Innaarsuit', 1607, 'Nej'],
            ['022160711010011', 2022, 'havgående', '010011', 'Reje - havgående licens', 11, 'Innaarsuit', 1607, None],
            ['022160712010012', 2022, 'kystnært', '010012', 'Reje - kystnær licens', 12, 'Innaarsuit', 1607, None],
            ['022160713010014', 2022, 'svalbard', '010014', 'Reje - Svalbard og Barentshavet', 13, 'Innaarsuit', 1607, None],
            ['022160710010029', 2022, 'havgående', '010029', 'Rødfisk', 10, 'Innaarsuit', 1607, None],
            ['022160710010030', 2022, 'indhandling', '010030', 'Rødfisk', 10, 'Innaarsuit', 1607, None],
            ['022160709010033', 2022, 'havgående', '010033', 'Sej', 9, 'Innaarsuit', 1607, None],
            ['022160709010034', 2022, 'indhandling', '010034', 'Sej', 9, 'Innaarsuit', 1607, None],
            ['022160702010023', 2022, None, '010023', 'Sild', 2, 'Innaarsuit', 1607, 'Ja'],
            ['022160702010024', 2022, None, '010024', 'Sild', 2, 'Innaarsuit', 1607, 'Nej'],
            ['022160707010027', 2022, 'havgående', '010027', 'Torsk', 7, 'Innaarsuit', 1607, None],
            ['022160707010028', 2022, 'indhandling', '010028', 'Torsk', 7, 'Innaarsuit', 1607, None]
        ]

        self.maxDiff = None
        self.assertEqual([[cell.value for cell in ws[row]] for row in range(1, ws.max_row+1)], expected)
