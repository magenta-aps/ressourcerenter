from django.core.management.base import BaseCommand
from django.utils.datetime_safe import date, datetime
from resmockup.models import (
    FormularFelt,
    BeregningsModelEksempel,
    BeregningsModelPrototype,
    Afgiftstabel,
    Afgiftsperiode,
    Indberetning,
    BeregnetIndberetning,
    Indberetter,
    FiskeArt,
    Kategori,
    SummeretBeregnetIndberetning,
)


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        # Opret alle out-of-the-box objekter her

        fisk1, created = FiskeArt.objects.get_or_create(
            navn="Sild", beskrivelse="Clupea harengus"
        )
        fisk2, created = FiskeArt.objects.get_or_create(
            navn="Makrel", beskrivelse="Scomber scombrus"
        )
        fisk3, created = FiskeArt.objects.get_or_create(
            navn="Torsk", beskrivelse="Gadus morhua"
        )
        fisk4, created = FiskeArt.objects.get_or_create(
            navn="Rejer", beskrivelse="Pandalus borealis"
        )

        kategori1, created = Kategori.objects.get_or_create(
            navn="Kystnært", beskrivelse="Kystnært fiskeri"
        )
        kategori2, created = Kategori.objects.get_or_create(
            navn="Dybhav", beskrivelse="Dybhavsfiskeri"
        )

        FormularFelt.objects.get_or_create(
            navn="Kommune", type=FormularFelt.TYPE_ENUM, valideringsregel=""
        )

        FormularFelt.objects.get_or_create(
            navn="Vægt", type=FormularFelt.TYPE_INT, valideringsregel=""
        )

        beregningsmodelproto1, created = BeregningsModelPrototype.objects.get_or_create(
            navn="Standard beregningsmodel", beskrivelse="Almindelig beregningsmodel"
        )

        beregningsmodel1, created = BeregningsModelEksempel.objects.get_or_create(
            prototype=beregningsmodelproto1,
            navn="Beregningsmodel 2019 (Forsøg 1)",
            beskrivelse="Beregningsmodel for 2019 (første forsøg)",
            justering_A=7,
            justering_B=50,
        )

        beregningsmodel2, created = BeregningsModelEksempel.objects.get_or_create(
            prototype=beregningsmodelproto1,
            navn="Beregningsmodel 2019 (Forsøg 2)",
            beskrivelse="Beregningsmodel for 2019 (andet forsøg)",
            justering_A=6,
            justering_B=60,
        )

        afgiftstabel1, created = Afgiftstabel.objects.get_or_create(
            navn="Afgiftstabel 2018",
            beskrivelse="Dette er den endelige afgiftstabel for 2018",
            kategori=kategori1,
        )

        indberetter1, created = Indberetter.objects.get_or_create(
            cpr_cvr_nummer="12345678",
            navn="TestPerson",
            email="test@magenta.dk",
            kontonummer="87654321",
            er_rederi=False,
            administrationsadresse_navn="Bæredygtigt Fiskeri A/S",
            administrationsadresse_adresse="Testvej 42",
            administrationsadresse_postnummer_by="3900 Nuuk",
        )

        afgiftsperiode1, created = Afgiftsperiode.objects.get_or_create(
            navn="2019",
            dato_fra=date(2019, 1, 1),
            dato_til=date(2019, 12, 31),
            beskrivelse="Afgiftsperioden for 2019",
            beregningsmodel=beregningsmodel1,
        )

        indberetning1, created = Indberetning.objects.get_or_create(
            indberetter=indberetter1,
            afgiftsperiode=afgiftsperiode1,
            indberetningstidspunkt=datetime(2019, 9, 1, 10, 18, 0),
            afgiftsberegningstidspunkt=datetime(2019, 3, 7, 12, 0, 0),
            kategori=kategori1,
            cpr_cvr="12345678",
            fartoejets_navn="M/S Baljen",
            fartoejets_hjemsted="Nuuk",
            indhandlings_eller_produktionsanlaeg="Nuuk Havn",
            indhandlers_cpr_cvr="22222222",
            fiskeart=fisk4,
            levende_vaegt=2000,
            indhandlet_vaegt=1800,
            vederlag_dkk=20000,
            salgspris_dkk=15000,
            salgsmaengde_vaegt=1800,
            yderligere_dokumentation="",
        )
        indberetning2, created = Indberetning.objects.get_or_create(
            indberetter=indberetter1,
            afgiftsperiode=afgiftsperiode1,
            indberetningstidspunkt=datetime(2019, 9, 6, 10, 18, 0),
            afgiftsberegningstidspunkt=datetime(2019, 9, 7, 12, 0, 0),
            kategori=kategori2,
            cpr_cvr="12345678",
            fartoejets_navn="M/S Baljen",
            fartoejets_hjemsted="Nuuk",
            indhandlings_eller_produktionsanlaeg="Nuuk Havn",
            indhandlers_cpr_cvr="22222222",
            fiskeart=fisk4,
            levende_vaegt=4000,
            indhandlet_vaegt=3800,
            vederlag_dkk=40000,
            salgspris_dkk=35000,
            salgsmaengde_vaegt=3800,
            yderligere_dokumentation="",
        )

        (
            summeretberegnetindberetning1,
            created,
        ) = SummeretBeregnetIndberetning.objects.get_or_create(
            justering=False,
            afgift_til_betaling=100,
            afstemt=False,
            bogfoert=False,
            sendt_til_prisme=False,
        )

        beregnetindberetning1, created = BeregnetIndberetning.objects.get_or_create(
            indberetning=indberetning1,
            summeret_beregnet_indberetning=summeretberegnetindberetning1,
            beregningsmodel=beregningsmodel1,
            afgiftstabel=afgiftstabel1,
            kladde=True,
            simuleret=True,
            transportpris_indgaar_i_salgspris=False,
            omregningsfaktor=1,
            afgiftsgrundlag=1,
        )
        beregnetindberetning2, created = BeregnetIndberetning.objects.get_or_create(
            indberetning=indberetning2,
            summeret_beregnet_indberetning=summeretberegnetindberetning1,
            beregningsmodel=beregningsmodel1,
            afgiftstabel=afgiftstabel1,
            kladde=True,
            simuleret=True,
            transportpris_indgaar_i_salgspris=False,
            omregningsfaktor=1,
            afgiftsgrundlag=1,
        )
