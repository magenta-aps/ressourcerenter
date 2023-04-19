import uuid

from django.test import TestCase, override_settings
from indberetning.forms import IndberetningsTypeSelectForm
from indberetning.forms import VirksomhedsAddressForm
from indberetning.forms import IndberetningsLinjeBeregningForm
from indberetning.forms import IndberetningsLinjeSkema1Form
from indberetning.forms import IndberetningsLinjeSkema2Form
from indberetning.forms import IndberetningsLinjeSkema3Form
from indberetning.models import Afgiftsperiode
from indberetning.models import SkemaType
from indberetning.models import ProduktType
from indberetning.models import Indhandlingssted


class CompanyContactTestForm(TestCase):
    def test_form_company_create_validation(self):
        """
        Test that validates the form for creation of company
        """

        # Try with an invalid E-mail
        form_data = {
            "kontakt_person": "test",
            "kontakt_email": "test",
            "kontakts_phone_nr": "test",
        }
        form = VirksomhedsAddressForm(data=form_data)
        self.assertFalse(form.is_valid())

        # Try with valid information
        form_data = {
            "kontakt_person": "test",
            "kontakt_email": "test@test.test",
            "kontakts_phone_nr": "test",
            "sted": Indhandlingssted.objects.first().uuid,
        }
        form = VirksomhedsAddressForm(data=form_data)
        self.assertTrue(form.is_valid())


class IndberetningSelectTestForm(TestCase):
    def setUp(self) -> None:
        self.periode = Afgiftsperiode.objects.get(navn_dk="4. kvartal 2021")
        self.skema = SkemaType.objects.get(
            navn_dk="Havgående fartøjer og kystnære rejefartøjer - producerende fartøjer"
        )

    def test_form_select_indberetningstype_only_skema(self):
        """
        Test selection of indberetningstype
        """

        form_data = {"skema": self.skema}
        form = IndberetningsTypeSelectForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_form_select_indberetningstype_only_periode(self):
        form_data = {"periode": self.periode}
        form = IndberetningsTypeSelectForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_form_select_indberetningstype_invalid_skema(self):
        form_data = {"skema": None, "periode": self.periode}
        form = IndberetningsTypeSelectForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_form_select_indberetningstype_invalid_periode(self):
        form_data = {"skema": self.skema, "periode": None}
        form = IndberetningsTypeSelectForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_form_select_indberetningstype_all_ok(self):
        form_data = {"skema": self.skema, "periode": self.periode}
        form = IndberetningsTypeSelectForm(data=form_data)
        self.assertTrue(form.is_valid())


@override_settings(DISABLE_CVR=False)
class BeregningslinjeTests(TestCase):
    """
    Test formvalidation IndberetningsLinjeBeregningForm
    """

    def setUp(self) -> None:
        self.produkttype = ProduktType.objects.get(
            navn_dk="Blåhvilling, grønlandsk fartøj",
        )

    def test_all_values_is_None(self):
        # All values missing
        form_data = {
            "produkttype": None,
            "produktvægt": None,
            "levende_vægt": None,
            "salgspris": None,
            "transporttillæg": "dummy",
            "bonus": None,
        }
        form = IndberetningsLinjeBeregningForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_all_values_is_positive(self):
        # Has all values
        form_data = {
            "produkttype": self.produkttype,
            "produktvægt": "100",
            "levende_vægt": "100",
            "salgspris": "100",
            "transporttillæg": "100",
            "bonus": "100",
        }
        form = IndberetningsLinjeBeregningForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_all_values_is_negative(self):
        # Has all negative values
        form_data = {
            "produkttype": self.produkttype,
            "produktvægt": "-100",
            "levende_vægt": "-100",
            "salgspris": "-100",
            "transporttillæg": "-100",
            "bonus": "-100",
        }
        form = IndberetningsLinjeBeregningForm(data=form_data)
        self.assertTrue(form.is_valid())

        # Has all negative string-values
        form_data = {
            "produkttype": self.produkttype,
            "produktvægt": "-100",
            "levende_vægt": "-100",
            "salgspris": "-100",
            "transporttillæg": "-100",
            "bonus": "-100",
        }
        form = IndberetningsLinjeBeregningForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_one_value_is_negative(self):
        # one of produktvægt, levende_vægt or salgspris is negative (invalid)
        form_data = {
            "produkttype": self.produkttype,
            "produktvægt": "-100",
            "levende_vægt": "100",
            "salgspris": "100",
            "transporttillæg": "100",
            "bonus": "100",
        }
        form = IndberetningsLinjeBeregningForm(data=form_data)
        self.assertFalse(form.is_valid())
        form_data = {
            "produkttype": self.produkttype,
            "produktvægt": "100",
            "levende_vægt": "-100",
            "salgspris": "100",
            "transporttillæg": "100",
            "bonus": "100",
        }
        form = IndberetningsLinjeBeregningForm(data=form_data)
        self.assertFalse(form.is_valid())
        form_data = {
            "produkttype": self.produkttype,
            "produktvægt": "100",
            "levende_vægt": "100",
            "salgspris": "-100",
            "transporttillæg": "100",
            "bonus": "100",
        }
        form = IndberetningsLinjeBeregningForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_one_value_is_0(self):
        # one of produktvægt, levende_vægt or salgspris is 0 (valid)
        form_data = {
            "produkttype": self.produkttype,
            "produktvægt": "0",
            "levende_vægt": "100",
            "salgspris": "100",
            "transporttillæg": "100",
            "bonus": "100",
        }
        form = IndberetningsLinjeBeregningForm(data=form_data)
        self.assertTrue(form.is_valid())
        form_data = {
            "produkttype": self.produkttype,
            "produktvægt": "100",
            "levende_vægt": "0",
            "salgspris": "100",
            "transporttillæg": "100",
            "bonus": "100",
        }
        form = IndberetningsLinjeBeregningForm(data=form_data)
        self.assertTrue(form.is_valid())
        form_data = {
            "produkttype": self.produkttype,
            "produktvægt": "100",
            "levende_vægt": "100",
            "salgspris": "0",
            "transporttillæg": "100",
            "bonus": "100",
        }
        form = IndberetningsLinjeBeregningForm(data=form_data)
        self.assertTrue(form.is_valid())


class IndberetningerTests(TestCase):
    def setUp(self) -> None:
        self.cvr = "12345678"
        Indhandlingssted.objects.create(navn="test", stedkode="1234")


class Indberetninger1Tests(IndberetningerTests):
    """
    Test the formular for skematype1
    """

    def setUp(self) -> None:
        super().setUp()
        self.first_ex_producttype = ProduktType.objects.get(
            fiskeart__skematype=1,
            fiskeart__navn_dk="Blåhvilling",
            fartoej_groenlandsk=True,
        )
        self.first_example_indhandlingssted = Indhandlingssted.objects.get(navn="test")

    def test_valid_positive_numbers(self):
        # Validate that a valid indberetning-form is accepted
        form_data = {
            "fartøj_navn": "test",
            "produkttype": self.first_ex_producttype.uuid,
            "levende_vægt": "100",
            "transporttillæg": "100",
            "produktvægt": "100",
            "indhandlingssted": self.first_example_indhandlingssted.uuid,
        }
        form = IndberetningsLinjeSkema1Form(cvr=self.cvr, data=form_data)
        self.assertTrue(form.is_valid())

    def test_valid_all_negative_numbers(self):
        # Add all negative values
        form_data = {
            "fartøj_navn": "test",
            "produkttype": self.first_ex_producttype.uuid,
            "levende_vægt": "-100",
            "transporttillæg": "-100",
            "produktvægt": "-100",
            "salgspris": "-100",
            "indhandlingssted": self.first_example_indhandlingssted.uuid,
        }
        form = IndberetningsLinjeSkema1Form(cvr=self.cvr, data=form_data)
        self.assertTrue(form.is_valid())

    def test_dummy_attributes(self):
        # Add dummy attribute, and validate that it is ignored
        form_data = {
            "fartøj_navn": "test",
            "produkttype": self.first_ex_producttype.uuid,
            "levende_vægt": "100",
            "transporttillæg": "100",
            "produktvægt": "100",
            "salgspris": "100",
            "dummy": "100",
            "indhandlingssted": self.first_example_indhandlingssted.uuid,
        }
        form = IndberetningsLinjeSkema1Form(cvr=self.cvr, data=form_data)
        self.assertTrue(form.is_valid())
        form_data = {
            "fartøj_navn": "test",
            "produkttype": self.first_ex_producttype.uuid,
            "levende_vægt": "100",
            "transporttillæg": "100",
            "produktvægt": "100",
            "salgspris": "100",
            "dummy": "-100",
            "indhandlingssted": self.first_example_indhandlingssted.uuid,
        }
        form = IndberetningsLinjeSkema1Form(cvr=self.cvr, data=form_data)
        self.assertTrue(form.is_valid())
        form_data = {
            "fartøj_navn": "test",
            "produkttype": self.first_ex_producttype.uuid,
            "levende_vægt": "100",
            "transporttillæg": "100",
            "produktvægt": "100",
            "salgspris": "100",
            "dummy": "abc",
            "indhandlingssted": self.first_example_indhandlingssted.uuid,
        }
        form = IndberetningsLinjeSkema1Form(cvr=self.cvr, data=form_data)
        self.assertTrue(form.is_valid())
        form_data = {
            "fartøj_navn": "test",
            "produkttype": self.first_ex_producttype.uuid,
            "levende_vægt": "100",
            "transporttillæg": "100",
            "produktvægt": "100",
            "salgspris": "100",
            "dummy": None,
            "indhandlingssted": self.first_example_indhandlingssted.uuid,
        }
        form = IndberetningsLinjeSkema1Form(cvr=self.cvr, data=form_data)
        self.assertTrue(form.is_valid())
        form_data = {
            "fartøj_navn": "test",
            "produkttype": self.first_ex_producttype.uuid,
            "levende_vægt": "100",
            "transporttillæg": "100",
            "produktvægt": "100",
            "salgspris": "100",
            "dummy": True,
            "indhandlingssted": self.first_example_indhandlingssted.uuid,
        }
        form = IndberetningsLinjeSkema1Form(cvr=self.cvr, data=form_data)
        self.assertTrue(form.is_valid())

    def test_only_one_negative_value(self):
        # Add only one negative value to produktvægt, levendevægt og salgspris
        form_data = {
            "fartøj_navn": "test",
            "produkttype": self.first_ex_producttype.uuid,
            "levende_vægt": "-100",
            "transporttillæg": "100",
            "produktvægt": "100",
            "salgspris": "100",
            "indhandlingssted": self.first_example_indhandlingssted.uuid,
        }
        form = IndberetningsLinjeSkema1Form(cvr=self.cvr, data=form_data)
        self.assertFalse(form.is_valid())
        form_data = {
            "fartøj_navn": "test",
            "produkttype": self.first_ex_producttype.uuid,
            "levende_vægt": "100",
            "transporttillæg": "100",
            "produktvægt": "-100",
            "salgspris": "100",
            "indhandlingssted": self.first_example_indhandlingssted.uuid,
        }
        form = IndberetningsLinjeSkema1Form(cvr=self.cvr, data=form_data)
        self.assertFalse(form.is_valid())
        form_data = {
            "fartøj_navn": "test",
            "produkttype": self.first_ex_producttype.uuid,
            "levende_vægt": "100",
            "transporttillæg": "100",
            "produktvægt": "100",
            "salgspris": "-100",
            "indhandlingssted": self.first_example_indhandlingssted.uuid,
        }
        form = IndberetningsLinjeSkema1Form(cvr=self.cvr, data=form_data)
        self.assertFalse(form.is_valid())

    def test_all_0_value(self):
        # Add all 0 values
        form_data = {
            "fartøj_navn": "test",
            "produkttype": self.first_ex_producttype.uuid,
            "levende_vægt": "0",
            "transporttillæg": "0",
            "produktvægt": "0",
            "salgspris": "0",
            "indhandlingssted": self.first_example_indhandlingssted.uuid,
        }
        form = IndberetningsLinjeSkema1Form(cvr=self.cvr, data=form_data)
        self.assertTrue(form.is_valid())

    def test_decimal_numbers(self):
        # Add decimal number as string
        form_data = {
            "fartøj_navn": "test",
            "produkttype": self.first_ex_producttype.uuid,
            "levende_vægt": "5,5",
            "transporttillæg": "5,5",
            "produktvægt": "5,5",
            "salgspris": "5,5",
            "indhandlingssted": self.first_example_indhandlingssted.uuid,
        }
        form = IndberetningsLinjeSkema1Form(cvr=self.cvr, data=form_data)
        self.assertTrue(form.is_valid())

    def test_one_invalid_string_value(self):
        # Add only one negative value to produktvægt, levendevægt og salgspris
        form_data = {
            "fartøj_navn": "test",
            "produkttype": self.first_ex_producttype.uuid,
            "levende_vægt": "abc",
            "transporttillæg": "100",
            "produktvægt": "100",
            "salgspris": "100",
            "indhandlingssted": self.first_example_indhandlingssted.uuid,
        }
        form = IndberetningsLinjeSkema1Form(cvr=self.cvr, data=form_data)
        self.assertFalse(form.is_valid())
        form_data = {
            "fartøj_navn": "test",
            "produkttype": self.first_ex_producttype.uuid,
            "levende_vægt": "100",
            "transporttillæg": "abc",
            "produktvægt": "100",
            "salgspris": "100",
            "indhandlingssted": self.first_example_indhandlingssted.uuid,
        }
        form = IndberetningsLinjeSkema1Form(cvr=self.cvr, data=form_data)
        self.assertFalse(form.is_valid())
        form_data = {
            "fartøj_navn": "test",
            "produkttype": self.first_ex_producttype.uuid,
            "levende_vægt": "100",
            "transporttillæg": "100",
            "produktvægt": "abc",
            "salgspris": "100",
            "indhandlingssted": self.first_example_indhandlingssted.uuid,
        }
        form = IndberetningsLinjeSkema1Form(cvr=self.cvr, data=form_data)
        self.assertFalse(form.is_valid())
        form_data = {
            "fartøj_navn": "test",
            "produkttype": self.first_ex_producttype.uuid,
            "levende_vægt": "100",
            "transporttillæg": "100",
            "produktvægt": "100",
            "salgspris": "abc",
            "indhandlingssted": self.first_example_indhandlingssted.uuid,
        }
        form = IndberetningsLinjeSkema1Form(cvr=self.cvr, data=form_data)
        self.assertFalse(form.is_valid())

    def test_invalid_product_type(self):
        # Validate that a unknown 'produkttype' is rejected
        form_data = {
            "fartøj_navn": "test",
            "produkttype": uuid.uuid4,
            "levende_vægt": "100",
            "indhandlingssted": self.first_example_indhandlingssted.uuid,
        }
        form = IndberetningsLinjeSkema1Form(cvr=self.cvr, data=form_data)
        self.assertFalse(form.is_valid())

    def test_invalid_indhandlingssted(self):
        # Validate that a unknown 'indhandlingssted' is rejected
        form_data = {
            "fartøj_navn": "test",
            "produkttype": self.first_ex_producttype.uuid,
            "levende_vægt": "100",
            "indhandlingssted": uuid.uuid4,
        }
        form = IndberetningsLinjeSkema1Form(cvr=self.cvr, data=form_data)
        self.assertFalse(form.is_valid())


class Indberetninger2Tests(IndberetningerTests):
    """
    Test the formular for skematype2
    """

    def setUp(self) -> None:
        super().setUp()
        self.first_ex_producttype = ProduktType.objects.get(
            fiskeart__skematype=2,
            fiskeart__navn_dk="Blåhvilling",
            fartoej_groenlandsk=True,
        )
        self.first_example_indhandlingssted = Indhandlingssted.objects.get(navn="test")

    def test_valid_positive_numbers(self):
        # Validate that a valid indberetning-form is accepted
        form_data = {
            "fartøj_navn": "test",
            "produkttype": self.first_ex_producttype.uuid,
            "levende_vægt": "100",
            "transporttillæg": "100",
            "produktvægt": "100",
            "bonus": "100",
            "indhandlingssted": self.first_example_indhandlingssted.uuid,
        }
        form = IndberetningsLinjeSkema2Form(cvr=self.cvr, data=form_data)
        self.assertTrue(form.is_valid())

    def test_valid_all_negative_numbers(self):
        # Add all negative values
        form_data = {
            "fartøj_navn": "test",
            "produkttype": self.first_ex_producttype.uuid,
            "levende_vægt": "-100",
            "transporttillæg": "-100",
            "produktvægt": "-100",
            "bonus": "-100",
            "salgspris": "-100",
            "indhandlingssted": self.first_example_indhandlingssted.uuid,
        }
        form = IndberetningsLinjeSkema2Form(cvr=self.cvr, data=form_data)
        self.assertTrue(form.is_valid())

    def test_dummy_attributes(self):
        # Add dummy attribute, and validate that it is ignored
        form_data = {
            "fartøj_navn": "test",
            "produkttype": self.first_ex_producttype.uuid,
            "levende_vægt": "100",
            "transporttillæg": "100",
            "produktvægt": "100",
            "bonus": "100",
            "salgspris": "100",
            "dummy": "100",
            "indhandlingssted": self.first_example_indhandlingssted.uuid,
        }
        form = IndberetningsLinjeSkema2Form(cvr=self.cvr, data=form_data)
        self.assertTrue(form.is_valid())
        form_data = {
            "fartøj_navn": "test",
            "produkttype": self.first_ex_producttype.uuid,
            "levende_vægt": "100",
            "transporttillæg": "100",
            "produktvægt": "100",
            "bonus": "100",
            "salgspris": "100",
            "dummy": "-100",
            "indhandlingssted": self.first_example_indhandlingssted.uuid,
        }
        form = IndberetningsLinjeSkema2Form(cvr=self.cvr, data=form_data)
        self.assertTrue(form.is_valid())
        form_data = {
            "fartøj_navn": "test",
            "produkttype": self.first_ex_producttype.uuid,
            "levende_vægt": "100",
            "transporttillæg": "100",
            "produktvægt": "100",
            "bonus": "100",
            "salgspris": "100",
            "dummy": "abc",
            "indhandlingssted": self.first_example_indhandlingssted.uuid,
        }
        form = IndberetningsLinjeSkema2Form(cvr=self.cvr, data=form_data)
        self.assertTrue(form.is_valid())
        form_data = {
            "fartøj_navn": "test",
            "produkttype": self.first_ex_producttype.uuid,
            "levende_vægt": "100",
            "transporttillæg": "100",
            "produktvægt": "100",
            "bonus": "100",
            "salgspris": "100",
            "dummy": None,
            "indhandlingssted": self.first_example_indhandlingssted.uuid,
        }
        form = IndberetningsLinjeSkema2Form(cvr=self.cvr, data=form_data)
        self.assertTrue(form.is_valid())
        form_data = {
            "fartøj_navn": "test",
            "produkttype": self.first_ex_producttype.uuid,
            "levende_vægt": "100",
            "transporttillæg": "100",
            "produktvægt": "100",
            "bonus": "100",
            "salgspris": "100",
            "dummy": True,
            "indhandlingssted": self.first_example_indhandlingssted.uuid,
        }
        form = IndberetningsLinjeSkema2Form(cvr=self.cvr, data=form_data)
        self.assertTrue(form.is_valid())

    def test_only_one_negative_value(self):
        # Add only one negative value to produktvægt, levendevægt og salgspris
        form_data = {
            "fartøj_navn": "test",
            "produkttype": self.first_ex_producttype.uuid,
            "levende_vægt": "-100",
            "transporttillæg": "100",
            "produktvægt": "100",
            "bonus": "100",
            "salgspris": "100",
            "indhandlingssted": self.first_example_indhandlingssted.uuid,
        }
        form = IndberetningsLinjeSkema2Form(cvr=self.cvr, data=form_data)
        self.assertFalse(form.is_valid())
        form_data = {
            "fartøj_navn": "test",
            "produkttype": self.first_ex_producttype.uuid,
            "levende_vægt": "100",
            "transporttillæg": "100",
            "produktvægt": "-100",
            "bonus": "100",
            "salgspris": "100",
            "indhandlingssted": self.first_example_indhandlingssted.uuid,
        }
        form = IndberetningsLinjeSkema2Form(cvr=self.cvr, data=form_data)
        self.assertFalse(form.is_valid())
        form_data = {
            "fartøj_navn": "test",
            "produkttype": self.first_ex_producttype.uuid,
            "levende_vægt": "100",
            "transporttillæg": "100",
            "produktvægt": "100",
            "bonus": "100",
            "salgspris": "-100",
            "indhandlingssted": self.first_example_indhandlingssted.uuid,
        }
        form = IndberetningsLinjeSkema2Form(cvr=self.cvr, data=form_data)
        self.assertFalse(form.is_valid())

    def test_all_0_value(self):
        # Add all 0 values
        form_data = {
            "fartøj_navn": "test",
            "produkttype": self.first_ex_producttype.uuid,
            "levende_vægt": "0",
            "transporttillæg": "0",
            "produktvægt": "0",
            "bonus": "0",
            "salgspris": "0",
            "indhandlingssted": self.first_example_indhandlingssted.uuid,
        }
        form = IndberetningsLinjeSkema2Form(cvr=self.cvr, data=form_data)
        self.assertTrue(form.is_valid())

    def test_decimal_numbers(self):
        # Add decimal number
        form_data = {
            "fartøj_navn": "test",
            "produkttype": self.first_ex_producttype.uuid,
            "levende_vægt": "5,5",
            "transporttillæg": "5,5",
            "produktvægt": "5,5",
            "bonus": "5,5",
            "salgspris": "5,5",
            "indhandlingssted": self.first_example_indhandlingssted.uuid,
        }
        form = IndberetningsLinjeSkema2Form(cvr=self.cvr, data=form_data)
        self.assertTrue(form.is_valid())

    def test_decimal_numbers_as_string(self):
        # Add decimal number as string
        form_data = {
            "fartøj_navn": "test",
            "produkttype": self.first_ex_producttype.uuid,
            "levende_vægt": "5.5",
            "transporttillæg": "5.5",
            "produktvægt": "5.5",
            "bonus": "5.5",
            "salgspris": "5.5",
            "indhandlingssted": self.first_example_indhandlingssted.uuid,
        }
        form = IndberetningsLinjeSkema2Form(cvr=self.cvr, data=form_data)
        self.assertTrue(form.is_valid())

    def test_one_invalid_string_value(self):
        # Add only one negative value to produktvægt, levendevægt og salgspris
        form_data = {
            "fartøj_navn": "test",
            "produkttype": self.first_ex_producttype.uuid,
            "levende_vægt": "abc",
            "transporttillæg": "100",
            "produktvægt": "100",
            "bonus": "100",
            "indhandlingssted": self.first_example_indhandlingssted.uuid,
        }
        form = IndberetningsLinjeSkema2Form(cvr=self.cvr, data=form_data)
        self.assertFalse(form.is_valid())
        form_data = {
            "fartøj_navn": "test",
            "produkttype": self.first_ex_producttype.uuid,
            "levende_vægt": "100",
            "transporttillæg": "abc",
            "produktvægt": "100",
            "bonus": "100",
            "indhandlingssted": self.first_example_indhandlingssted.uuid,
        }
        form = IndberetningsLinjeSkema2Form(cvr=self.cvr, data=form_data)
        self.assertFalse(form.is_valid())
        form_data = {
            "fartøj_navn": "test",
            "produkttype": self.first_ex_producttype.uuid,
            "levende_vægt": "100",
            "transporttillæg": "100",
            "produktvægt": "abc",
            "bonus": "100",
            "indhandlingssted": self.first_example_indhandlingssted.uuid,
        }
        form = IndberetningsLinjeSkema2Form(cvr=self.cvr, data=form_data)
        self.assertFalse(form.is_valid())

    def test_invalid_product_type(self):
        # Validate that a unknown 'produkttype' is rejected
        form_data = {
            "fartøj_navn": "test",
            "produkttype": uuid.uuid4,
            "levende_vægt": "100",
            "indhandlingssted": self.first_example_indhandlingssted.uuid,
        }
        form = IndberetningsLinjeSkema2Form(cvr=self.cvr, data=form_data)
        self.assertFalse(form.is_valid())

    def test_invalid_indhandlingssted(self):
        # Validate that a unknown 'indhandlingssted' is rejected
        form_data = {
            "fartøj_navn": "test",
            "produkttype": self.first_ex_producttype.uuid,
            "levende_vægt": "100",
            "indhandlingssted": uuid.uuid4,
        }
        form = IndberetningsLinjeSkema2Form(cvr=self.cvr, data=form_data)
        self.assertFalse(form.is_valid())


class Indberetninger3Tests(IndberetningerTests):
    """
    Test the formular for skematype3
    """

    def setUp(self) -> None:
        super().setUp()
        self.first_ex_producttype = ProduktType.objects.get(
            fiskeart__skematype=3, fiskeart__navn_dk="Hellefisk", gruppe=None
        )
        self.first_example_indhandlingssted = Indhandlingssted.objects.get(navn="test")

    def test_valid_positive_numbers(self):
        # Validate that a valid indberetning-form is accepted
        form_data = {
            "produkttype": self.first_ex_producttype.uuid,
            "levende_vægt": "100",
            "transporttillæg": "100",
            "bonus": "100",
            "indhandlingssted": self.first_example_indhandlingssted.uuid,
        }
        form = IndberetningsLinjeSkema3Form(cvr=self.cvr, data=form_data)
        self.assertTrue(form.is_valid())

    def test_valid_all_negative_numbers(self):
        # Add all negative values
        form_data = {
            "produkttype": self.first_ex_producttype.uuid,
            "levende_vægt": "-100",
            "transporttillæg": "-100",
            "bonus": "-100",
            "salgspris": "-100",
            "indhandlingssted": self.first_example_indhandlingssted.uuid,
        }
        form = IndberetningsLinjeSkema3Form(cvr=self.cvr, data=form_data)
        self.assertTrue(form.is_valid())

    def test_dummy_attributes(self):
        # Add dummy attribute, and validate that it is ignored
        form_data = {
            "produkttype": self.first_ex_producttype.uuid,
            "levende_vægt": "100",
            "transporttillæg": "100",
            "bonus": "100",
            "salgspris": "100",
            "dummy": "100",
            "indhandlingssted": self.first_example_indhandlingssted.uuid,
        }
        form = IndberetningsLinjeSkema3Form(cvr=self.cvr, data=form_data)
        self.assertTrue(form.is_valid())
        form_data = {
            "produkttype": self.first_ex_producttype.uuid,
            "levende_vægt": "100",
            "transporttillæg": "100",
            "bonus": "100",
            "salgspris": "100",
            "dummy": "-100",
            "indhandlingssted": self.first_example_indhandlingssted.uuid,
        }
        form = IndberetningsLinjeSkema3Form(cvr=self.cvr, data=form_data)
        self.assertTrue(form.is_valid())
        form_data = {
            "produkttype": self.first_ex_producttype.uuid,
            "levende_vægt": "100",
            "transporttillæg": "100",
            "bonus": "100",
            "salgspris": "100",
            "dummy": "abc",
            "indhandlingssted": self.first_example_indhandlingssted.uuid,
        }
        form = IndberetningsLinjeSkema3Form(cvr=self.cvr, data=form_data)
        self.assertTrue(form.is_valid())
        form_data = {
            "produkttype": self.first_ex_producttype.uuid,
            "levende_vægt": "100",
            "transporttillæg": "100",
            "bonus": "100",
            "salgspris": "100",
            "dummy": None,
            "indhandlingssted": self.first_example_indhandlingssted.uuid,
        }
        form = IndberetningsLinjeSkema3Form(cvr=self.cvr, data=form_data)
        self.assertTrue(form.is_valid())
        form_data = {
            "produkttype": self.first_ex_producttype.uuid,
            "levende_vægt": "100",
            "transporttillæg": "100",
            "bonus": "100",
            "salgspris": "100",
            "dummy": True,
            "indhandlingssted": self.first_example_indhandlingssted.uuid,
        }
        form = IndberetningsLinjeSkema3Form(cvr=self.cvr, data=form_data)
        self.assertTrue(form.is_valid())

    def test_only_one_negative_value(self):
        # Add only one negative value to produktvægt og salgspris
        form_data = {
            "produkttype": self.first_ex_producttype.uuid,
            "levende_vægt": "-100",
            "transporttillæg": "100",
            "bonus": "100",
            "salgspris": "100",
            "indhandlingssted": self.first_example_indhandlingssted.uuid,
        }
        form = IndberetningsLinjeSkema3Form(cvr=self.cvr, data=form_data)
        self.assertFalse(form.is_valid())
        form_data = {
            "produkttype": self.first_ex_producttype.uuid,
            "levende_vægt": "100",
            "transporttillæg": "100",
            "bonus": "100",
            "salgspris": "-100",
            "indhandlingssted": self.first_example_indhandlingssted.uuid,
        }
        form = IndberetningsLinjeSkema3Form(cvr=self.cvr, data=form_data)
        self.assertFalse(form.is_valid())

    def test_all_0_value(self):
        # Add all 0 values
        form_data = {
            "produkttype": self.first_ex_producttype.uuid,
            "levende_vægt": "0",
            "transporttillæg": "0",
            "bonus": "0",
            "salgspris": "0",
            "indhandlingssted": self.first_example_indhandlingssted.uuid,
        }
        form = IndberetningsLinjeSkema3Form(cvr=self.cvr, data=form_data)
        self.assertTrue(form.is_valid())

    def test_decimal_numbers(self):
        # Add decimal number
        form_data = {
            "produkttype": self.first_ex_producttype.uuid,
            "levende_vægt": "5,5",
            "transporttillæg": "5,5",
            "bonus": "5,5",
            "salgspris": "5,5",
            "indhandlingssted": self.first_example_indhandlingssted.uuid,
        }
        form = IndberetningsLinjeSkema3Form(cvr=self.cvr, data=form_data)
        self.assertTrue(form.is_valid())

    def test_decimal_numbers_as_string(self):
        # Add decimal number as string
        form_data = {
            "produkttype": self.first_ex_producttype.uuid,
            "levende_vægt": "5.5",
            "transporttillæg": "5.5",
            "bonus": "5.5",
            "salgspris": "5.5",
            "indhandlingssted": self.first_example_indhandlingssted.uuid,
        }
        form = IndberetningsLinjeSkema3Form(cvr=self.cvr, data=form_data)
        self.assertTrue(form.is_valid())

    def test_one_invalid_string_value(self):
        # Add only one negative value to produktvægt, levendevægt og salgspris
        form_data = {
            "produkttype": self.first_ex_producttype.uuid,
            "levende_vægt": "abc",
            "transporttillæg": "100",
            "bonus": "100",
            "salgspris": "100",
            "indhandlingssted": self.first_example_indhandlingssted.uuid,
        }
        form = IndberetningsLinjeSkema3Form(cvr=self.cvr, data=form_data)
        self.assertFalse(form.is_valid())
        form_data = {
            "produkttype": self.first_ex_producttype.uuid,
            "levende_vægt": "100",
            "transporttillæg": "abc",
            "bonus": "100",
            "salgspris": "100",
            "indhandlingssted": self.first_example_indhandlingssted.uuid,
        }
        form = IndberetningsLinjeSkema3Form(cvr=self.cvr, data=form_data)
        self.assertFalse(form.is_valid())
        form_data = {
            "produkttype": self.first_ex_producttype.uuid,
            "levende_vægt": "100",
            "transporttillæg": "100",
            "bonus": "abc",
            "salgspris": "100",
            "indhandlingssted": self.first_example_indhandlingssted.uuid,
        }
        form = IndberetningsLinjeSkema3Form(cvr=self.cvr, data=form_data)
        self.assertFalse(form.is_valid())
        form_data = {
            "produkttype": self.first_ex_producttype.uuid,
            "levende_vægt": "100",
            "transporttillæg": "100",
            "bonus": "100",
            "salgspris": "abc",
            "indhandlingssted": self.first_example_indhandlingssted.uuid,
        }
        form = IndberetningsLinjeSkema3Form(cvr=self.cvr, data=form_data)
        self.assertFalse(form.is_valid())

    def test_invalid_product_type(self):
        # Validate that a unknown 'produkttype' is rejected
        form_data = {
            "produkttype": uuid.uuid4,
            "levende_vægt": "100",
            "indhandlingssted": self.first_example_indhandlingssted.uuid,
        }
        form = IndberetningsLinjeSkema3Form(cvr=self.cvr, data=form_data)
        self.assertFalse(form.is_valid())

    def test_invalid_indhandlingssted(self):
        # Validate that a unknown 'indhandlingssted' is rejected
        form_data = {
            "produkttype": self.first_ex_producttype.uuid,
            "levende_vægt": "100",
            "indhandlingssted": uuid.uuid4,
        }
        form = IndberetningsLinjeSkema3Form(cvr=self.cvr, data=form_data)
        self.assertFalse(form.is_valid())
