from django import forms
from django.core.exceptions import ValidationError
from django.forms.widgets import TextInput
from django.utils.translation import gettext as _


class LocalizedDecimalField(forms.DecimalField):
    def __init__(self, max_value=None, min_value=None, max_digits=None, decimal_places=None, **kwargs):
        kwargs['widget'] = TextInput  # use text input to avoid input type=number
        kwargs['localize'] = True  # allow localized values such as 1.200,24
        super(LocalizedDecimalField, self).__init__(max_value=max_value,
                                                    min_value=min_value,
                                                    max_digits=max_digits,
                                                    decimal_places=decimal_places,
                                                    **kwargs)

    def to_python(self, value):
        if '.' in str(value):
            raise ValidationError(_('Tallet må ikke indeholde punktum, kun komma'), code='invalid')
        return super().to_python(value)


class DateInput(forms.DateInput):
    input_type = 'date'

    def __init__(self, **kwargs):
        kwargs["format"] = "%Y-%m-%d"
        super().__init__(**kwargs)
