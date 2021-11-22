from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import re
cvr_re = re.compile('^[0-9]{8}$')
cpr_re = re.compile('^[0-9]{10}$')


def validate_cvr(value):
    if not cvr_re.match(value):
        raise ValidationError(
            _('CVR nr. skal indeholde 8 tal'),
        )


def validate_cpr(value):
    if not cpr_re.match(value):
        raise ValidationError(
            _('CPR nr. skal indeholde 10 tal')
        )
