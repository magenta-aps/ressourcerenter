import datetime

from administration.models import FiskeArt
from django.test import TestCase
from indberetning.models import (
    Afgiftsperiode,
    Indberetning,
    IndberetningLinje,
    Indhandlingssted,
    SkemaType,
    Virksomhed,
)


class RatenummerTest(TestCase):
    def setUp(self) -> None:
        self.virksomhed1 = Virksomhed.objects.create(cvr="00000001")
        self.virksomhed2 = Virksomhed.objects.create(cvr="00000002")
        self.periode1 = Afgiftsperiode.objects.create(
            dato_fra=datetime.date(2023, 1, 1), dato_til=datetime.date(2023, 3, 31)
        )
        self.periode2 = Afgiftsperiode.objects.create(
            dato_fra=datetime.date(2023, 4, 1), dato_til=datetime.date(2023, 6, 30)
        )
        self.skematype1 = SkemaType.objects.get(id=1)
        self.skematype2 = SkemaType.objects.get(id=2)
        self.indhandlingssted1 = Indhandlingssted.objects.all()[0]
        self.indhandlingssted2 = Indhandlingssted.objects.all()[1]
        self.fiskeart1 = FiskeArt.objects.get(navn_dk="Torsk")
        self.produkttype1a = self.fiskeart1.produkttype_set.all()[0]
        self.produkttype1b = self.fiskeart1.produkttype_set.all()[1]
        self.fiskeart2 = FiskeArt.objects.get(navn_dk="Sild")
        self.produkttype2a = self.fiskeart2.produkttype_set.all()[0]
        self.produkttype2b = self.fiskeart2.produkttype_set.all()[1]

    def test_ratenummer_same_data(self):
        indberetning1 = Indberetning.objects.create(
            skematype=self.skematype1,
            virksomhed=self.virksomhed1,
            afgiftsperiode=self.periode1,
        )
        linje1 = IndberetningLinje.objects.create(
            indberetning=indberetning1,
            fartøj_navn="Fartøj1",
            indhandlingssted=self.indhandlingssted1,
            produkttype=self.produkttype1a,
            levende_vægt=1000,
            salgspris=1000,
        )
        self.assertEqual("100", linje1.ratenummer)
        linje2 = IndberetningLinje.objects.create(
            indberetning=indberetning1,
            fartøj_navn="Fartøj1",
            indhandlingssted=self.indhandlingssted1,
            produkttype=self.produkttype1a,
            levende_vægt=1000,
            salgspris=1000,
        )
        self.assertEqual("100", linje2.ratenummer)
        linje3 = IndberetningLinje.objects.create(
            indberetning=indberetning1,
            fartøj_navn="Fartøj1",
            indhandlingssted=self.indhandlingssted1,
            produkttype=self.produkttype1a,
            levende_vægt=-1000,
            salgspris=-1000,
        )
        self.assertEqual("100", linje3.ratenummer)

    def test_ratenummer_different_product(self):
        indberetning1 = Indberetning.objects.create(
            skematype=self.skematype1,
            virksomhed=self.virksomhed1,
            afgiftsperiode=self.periode1,
        )
        linje1 = IndberetningLinje.objects.create(
            indberetning=indberetning1,
            fartøj_navn="Fartøj1",
            indhandlingssted=self.indhandlingssted1,
            produkttype=self.produkttype1a,
            levende_vægt=1000,
            salgspris=1000,
        )
        self.assertEqual("100", linje1.ratenummer)
        linje2 = IndberetningLinje.objects.create(
            indberetning=indberetning1,
            fartøj_navn="Fartøj1",
            indhandlingssted=self.indhandlingssted1,
            produkttype=self.produkttype1b,
            levende_vægt=1000,
            salgspris=1000,
        )
        self.assertEqual("101", linje2.ratenummer)

    def test_ratenummer_different_fish(self):
        indberetning1 = Indberetning.objects.create(
            skematype=self.skematype1,
            virksomhed=self.virksomhed1,
            afgiftsperiode=self.periode1,
        )
        linje1 = IndberetningLinje.objects.create(
            indberetning=indberetning1,
            fartøj_navn="Fartøj1",
            indhandlingssted=self.indhandlingssted1,
            produkttype=self.produkttype1a,
            levende_vægt=1000,
            salgspris=1000,
        )
        self.assertEqual("100", linje1.ratenummer)
        linje2 = IndberetningLinje.objects.create(
            indberetning=indberetning1,
            fartøj_navn="Fartøj1",
            indhandlingssted=self.indhandlingssted1,
            produkttype=self.produkttype2a,
            levende_vægt=1000,
            salgspris=1000,
        )
        self.assertEqual("100", linje2.ratenummer)

    def test_ratenummer_different_vessel(self):
        indberetning1 = Indberetning.objects.create(
            skematype=self.skematype1,
            virksomhed=self.virksomhed1,
            afgiftsperiode=self.periode1,
        )
        linje1 = IndberetningLinje.objects.create(
            indberetning=indberetning1,
            fartøj_navn="Fartøj1",
            indhandlingssted=self.indhandlingssted1,
            produkttype=self.produkttype1a,
            levende_vægt=1000,
            salgspris=1000,
        )
        self.assertEqual("100", linje1.ratenummer)
        linje2 = IndberetningLinje.objects.create(
            indberetning=indberetning1,
            fartøj_navn="Fartøj2",
            indhandlingssted=self.indhandlingssted1,
            produkttype=self.produkttype1a,
            levende_vægt=1000,
            salgspris=1000,
        )
        self.assertEqual("101", linje2.ratenummer)

    def test_ratenummer_different_place(self):
        indberetning1 = Indberetning.objects.create(
            skematype=self.skematype1,
            virksomhed=self.virksomhed1,
            afgiftsperiode=self.periode1,
        )
        linje1 = IndberetningLinje.objects.create(
            indberetning=indberetning1,
            fartøj_navn="Fartøj1",
            indhandlingssted=self.indhandlingssted1,
            produkttype=self.produkttype1a,
            levende_vægt=1000,
            salgspris=1000,
        )
        self.assertEqual("100", linje1.ratenummer)
        linje2 = IndberetningLinje.objects.create(
            indberetning=indberetning1,
            fartøj_navn="Fartøj1",
            indhandlingssted=self.indhandlingssted2,
            produkttype=self.produkttype1a,
            levende_vægt=1000,
            salgspris=1000,
        )
        self.assertEqual("101", linje2.ratenummer)

    def test_ratenummer_different_cvr(self):
        indberetning1 = Indberetning.objects.create(
            skematype=self.skematype1,
            virksomhed=self.virksomhed1,
            afgiftsperiode=self.periode1,
        )
        linje1 = IndberetningLinje.objects.create(
            indberetning=indberetning1,
            fartøj_navn="Fartøj1",
            indhandlingssted=self.indhandlingssted1,
            produkttype=self.produkttype1a,
            levende_vægt=1000,
            salgspris=1000,
        )
        self.assertEqual("100", linje1.ratenummer)
        indberetning2 = Indberetning.objects.create(
            skematype=self.skematype1,
            virksomhed=self.virksomhed2,
            afgiftsperiode=self.periode1,
        )
        linje2 = IndberetningLinje.objects.create(
            indberetning=indberetning2,
            fartøj_navn="Fartøj1",
            indhandlingssted=self.indhandlingssted1,
            produkttype=self.produkttype1a,
            levende_vægt=1000,
            salgspris=1000,
        )
        self.assertEqual("100", linje2.ratenummer)

    def test_ratenummer_different_indberetning(self):
        indberetning1 = Indberetning.objects.create(
            skematype=self.skematype1,
            virksomhed=self.virksomhed1,
            afgiftsperiode=self.periode1,
        )
        linje1 = IndberetningLinje.objects.create(
            indberetning=indberetning1,
            fartøj_navn="Fartøj1",
            indhandlingssted=self.indhandlingssted1,
            produkttype=self.produkttype1a,
            levende_vægt=1000,
            salgspris=1000,
        )
        self.assertEqual("100", linje1.ratenummer)
        indberetning2 = Indberetning.objects.create(
            skematype=self.skematype1,
            virksomhed=self.virksomhed1,
            afgiftsperiode=self.periode1,
        )
        linje2 = IndberetningLinje.objects.create(
            indberetning=indberetning2,
            fartøj_navn="Fartøj1",
            indhandlingssted=self.indhandlingssted1,
            produkttype=self.produkttype1a,
            levende_vægt=1000,
            salgspris=1000,
        )
        self.assertEqual("101", linje2.ratenummer)
