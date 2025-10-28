from administration.models import Afgiftsperiode
from administration.models import BeregningsModel2021
from administration.models import FiskeArt
from administration.models import ProduktType
from administration.models import SkemaType
from datetime import date
from decimal import Decimal
from django.test import TestCase
from indberetning.models import IndberetningLinje
from indberetning.models import Virksomhed, Indberetning
from statistik.forms import StatistikForm
from statistik.views import StatistikView


class StatistikTestCase(TestCase):
    def setUp(self):
        virksomhed = Virksomhed.objects.create(cvr=12345678)
        beregningsmodel = BeregningsModel2021.objects.create(
            navn="TestBeregningsModel",
        )
        afgiftsperiode = Afgiftsperiode.objects.get(dato_fra=date(2022, 1, 1))
        afgiftsperiode.beregningsmodel = beregningsmodel
        afgiftsperiode.save()
        eksport_indberetning = Indberetning.objects.create(
            virksomhed=virksomhed,
            skematype=SkemaType.objects.get(id=1),
            afgiftsperiode=afgiftsperiode,
            afstemt=True,
        )
        IndberetningLinje.objects.create(
            indberetning=eksport_indberetning,
            produkttype=ProduktType.objects.get(navn_dk="Hellefisk - Filet"),
            produktvægt=100,
            levende_vægt=140,
            bonus=0,
        )
        IndberetningLinje.objects.create(
            indberetning=eksport_indberetning,
            produkttype=ProduktType.objects.get(navn_dk="Hellefisk - Biprodukter"),
            produktvægt=50,
            levende_vægt=80,
        )
        indhandling_indberetning = Indberetning.objects.create(
            virksomhed=virksomhed,
            skematype=SkemaType.objects.get(id=2),
            afgiftsperiode=afgiftsperiode,
            afstemt=True,
        )
        IndberetningLinje.objects.create(
            indberetning=indhandling_indberetning,
            produkttype=ProduktType.objects.get(navn_dk="Hellefisk"),
            produktvægt=1000,
            levende_vægt=2000,
            bonus=1000,
        )
        self.view = StatistikView()

    def get_form_result(self, **fields):
        form = StatistikForm(
            data={
                "skematype_3": 0,
                "years": [2022],
                "quarter_starting_month": [1],
                "enhed": ["levende_ton"],
                **{
                    key: values if type(values) is list else [values]
                    for key, values in fields.items()
                },
            }
        )
        self.assertTrue(form.is_valid(), form.errors)
        resultat = self.view.get_resultat(form)
        return [
            {resultat["headings"][i]: item["value"] for i, item in enumerate(row)}
            for row in resultat["rows"]
        ]

    def test_fiskeart_eksport_explicit_indberetningstype(self):
        # Test at eksplicit indberetningstype=eksport og fiskeart_eksport returnerer kun eksporterede hellefisk
        resultat = self.get_form_result(
            indberetningstype="Eksport",
            fiskeart_eksport=FiskeArt.objects.get(navn_dk="Hellefisk").uuid,
        )
        self.assertEqual(1, len(resultat))
        self.assertEqual(
            resultat[0],
            {
                "År": "2022",
                "Kvartal": "1. kvartal",
                "Indberetningstype": "Eksport",
                "Fiskeart (eksport)": "Hellefisk",
                "Levende vægt tons": Decimal("0.22"),
            },
        )

        # Test at eksplicit indberetningstype=eksport og fiskeart_eksport returnerer kun eksporterede hellefisk, selvom fiskeart_indhandling også er sat
        resultat = self.get_form_result(
            indberetningstype="Eksport",
            fiskeart_eksport=FiskeArt.objects.get(navn_dk="Hellefisk").uuid,
            fiskeart_indhandling=FiskeArt.objects.get(navn_dk="Hellefisk").uuid,
        )
        self.assertEqual(1, len(resultat))
        self.assertEqual(
            resultat[0],
            {
                "År": "2022",
                "Kvartal": "1. kvartal",
                "Indberetningstype": "Eksport",
                "Fiskeart (eksport)": "Hellefisk",
                "Fiskeart (indhandling)": "",
                "Levende vægt tons": Decimal("0.22"),
            },
        )

    def test_fiskeart_indhandling_explicit_indberetningstype(self):
        # Test at eksplicit indberetningstype=indhandling og fiskeart_indhandling returnerer kun indhandlede hellefisk
        resultat = self.get_form_result(
            indberetningstype="Indhandling",
            fiskeart_indhandling=FiskeArt.objects.get(navn_dk="Hellefisk").uuid,
        )
        self.assertEqual(1, len(resultat))
        self.assertEqual(
            resultat[0],
            {
                "År": "2022",
                "Kvartal": "1. kvartal",
                "Indberetningstype": "Indhandling",
                "Fiskeart (indhandling)": "Hellefisk",
                "Levende vægt tons": Decimal("2.0"),
            },
        )

        # Test at eksplicit indberetningstype=indhandling og fiskeart_indhandling returnerer kun indhandlede hellefisk, selvom fiskeart_eksport også er sat
        resultat = self.get_form_result(
            indberetningstype="Indhandling",
            fiskeart_eksport=FiskeArt.objects.get(navn_dk="Hellefisk").uuid,
            fiskeart_indhandling=FiskeArt.objects.get(navn_dk="Hellefisk").uuid,
        )
        self.assertEqual(1, len(resultat))
        self.assertEqual(
            resultat[0],
            {
                "År": "2022",
                "Kvartal": "1. kvartal",
                "Indberetningstype": "Indhandling",
                "Fiskeart (eksport)": "",
                "Fiskeart (indhandling)": "Hellefisk",
                "Levende vægt tons": Decimal("2.0"),
            },
        )

        # Test at eksplicit indberetningstype=indhandling og fiskeart_indhandling returnerer kun indhandlede hellefisk, selvom produkttype_eksport er sat
        resultat = self.get_form_result(
            indberetningstype="Indhandling",
            fiskeart_indhandling=FiskeArt.objects.get(navn_dk="Hellefisk").uuid,
            produkttype_eksport=ProduktType.objects.get(
                navn_dk="Hellefisk - Hel fisk"
            ).uuid,
        )
        self.assertEqual(1, len(resultat))
        self.assertEqual(
            resultat[0],
            {
                "År": "2022",
                "Kvartal": "1. kvartal",
                "Indberetningstype": "Indhandling",
                "Fiskeart (indhandling)": "Hellefisk",
                "Produkttype (eksport)": "",
                "Levende vægt tons": Decimal("2.0"),
            },
        )

    def test_fiskeart_eksport_unset_indberetningstype(self):
        # Test at eksplicit fiskeart_eksport returnerer også indhandlede fisk
        resultat = self.get_form_result(
            fiskeart_eksport=FiskeArt.objects.get(navn_dk="Hellefisk").uuid,
        )
        self.assertEqual(2, len(resultat))
        self.assertEqual(
            resultat[0],
            {
                "År": "2022",
                "Kvartal": "1. kvartal",
                "Fiskeart (eksport)": "",
                "Levende vægt tons": Decimal("2.0"),
            },
        )  # indhandling
        self.assertEqual(
            resultat[1],
            {
                "År": "2022",
                "Kvartal": "1. kvartal",
                "Fiskeart (eksport)": "Hellefisk",
                "Levende vægt tons": Decimal("0.22"),
            },
        )  # eksport

    def test_fiskeart_indhandling_unset_indberetningstype(self):
        # Test at eksplicit fiskeart_indhandling returnerer også eksporterede fisk
        resultat = self.get_form_result(
            fiskeart_indhandling=FiskeArt.objects.get(navn_dk="Hellefisk").uuid,
        )
        self.assertEqual(2, len(resultat))
        self.assertEqual(
            resultat[0],
            {
                "År": "2022",
                "Kvartal": "1. kvartal",
                "Fiskeart (indhandling)": "",
                "Levende vægt tons": Decimal("0.22"),
            },
        )  # eksport
        self.assertEqual(
            resultat[1],
            {
                "År": "2022",
                "Kvartal": "1. kvartal",
                "Fiskeart (indhandling)": "Hellefisk",
                "Levende vægt tons": Decimal("2.0"),
            },
        )  # indhandling

    def test_fiskeart_eksport_indhandling_unset_indberetningstype(self):
        # Test at eksplicit fiskeart_eksport og fiskeart_indhandling returnerer både eksporterede og indhandlede fisk
        resultat = self.get_form_result(
            fiskeart_eksport=FiskeArt.objects.get(navn_dk="Hellefisk").uuid,
            fiskeart_indhandling=FiskeArt.objects.get(navn_dk="Hellefisk").uuid,
        )
        self.assertEqual(2, len(resultat))
        self.assertEqual(
            resultat[0],
            {
                "År": "2022",
                "Kvartal": "1. kvartal",
                "Fiskeart (eksport)": "",
                "Fiskeart (indhandling)": "Hellefisk",
                "Levende vægt tons": Decimal("2.0"),
            },
        )  # indhandling
        self.assertEqual(
            resultat[1],
            {
                "År": "2022",
                "Kvartal": "1. kvartal",
                "Fiskeart (eksport)": "Hellefisk",
                "Fiskeart (indhandling)": "",
                "Levende vægt tons": Decimal("0.22"),
            },
        )  # eksport

    def test_bonus_disregards_weight(self):
        resultat = self.get_form_result(
            fiskeart_eksport=FiskeArt.objects.get(navn_dk="Hellefisk").uuid,
            fiskeart_indhandling=FiskeArt.objects.get(navn_dk="Hellefisk").uuid,
        )
        self.assertEqual(resultat[0], {'År': '2022', 'Kvartal': '1. kvartal', 'Fiskeart (eksport)': '', 'Fiskeart (indhandling)': 'Hellefisk', 'Levende vægt tons': Decimal('2.00')})
        self.assertEqual(resultat[1], {'År': '2022', 'Kvartal': '1. kvartal', 'Fiskeart (eksport)': 'Hellefisk', 'Fiskeart (indhandling)': '', 'Levende vægt tons': Decimal('0.22')})

        # Indhandlingslinjen har bonus, forvent nulstilling af vægt
        resultat = self.get_form_result(
            disregard_bonus_reports="1",
            fiskeart_eksport=FiskeArt.objects.get(navn_dk="Hellefisk").uuid,
            fiskeart_indhandling=FiskeArt.objects.get(navn_dk="Hellefisk").uuid,
        )
        self.assertEqual(resultat[0], {'År': '2022', 'Kvartal': '1. kvartal', 'Fiskeart (eksport)': '', 'Fiskeart (indhandling)': 'Hellefisk', 'Levende vægt tons': Decimal('0.00')})
        self.assertEqual(resultat[1], {'År': '2022', 'Kvartal': '1. kvartal', 'Fiskeart (eksport)': 'Hellefisk', 'Fiskeart (indhandling)': '', 'Levende vægt tons': Decimal('0.22')})
